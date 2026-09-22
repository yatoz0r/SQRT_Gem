"""Unit tests for the entire updater subsystem: models, manifest fetcher, download manager, and installer runner."""

import hashlib
import json
import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.updater.models import parse_semver, PlatformAsset, UpdateInfo
from src.updater.manifest_fetcher import ManifestFetcher
from src.updater.download_manager import (
    calculate_sha256,
    DownloadManager,
    DownloadWorker,
    ChecksumMismatchError,
    DownloadCancelledError,
)
from src.updater.installer_runner import InstallerRunner
from src.updater.update_checker import UpdateChecker


# ==========================================
# 1. SemVer & Models Tests
# ==========================================

def test_parse_semver_variations():
    assert parse_semver("1.2.3") == (1, 2, 3)
    assert parse_semver("v2.1.0") == (2, 1, 0)
    assert parse_semver("1.0.0-beta.1+exp.sha.5114f85") == (1, 0, 0)
    assert parse_semver("3.5") == (3, 5, 0)
    assert parse_semver("4") == (4, 0, 0)
    assert parse_semver("") == (0, 0, 0)
    assert parse_semver(None) == (0, 0, 0)
    assert parse_semver("1.invalid.3") == (1, 0, 3)


def test_platform_asset_serialization():
    data = {
        "platform": "windows",
        "filename": "setup.msi",
        "download_url": "https://example.com/setup.msi",
        "sha256": "ABCDEF123456",
        "file_size": 1024
    }
    asset = PlatformAsset.from_dict(data)
    assert asset.platform == "windows"
    assert asset.filename == "setup.msi"
    assert asset.download_url == "https://example.com/setup.msi"
    assert asset.sha256 == "abcdef123456"
    assert asset.file_size == 1024

    serialized = asset.to_dict()
    assert serialized["platform"] == "windows"
    assert serialized["sha256"] == "abcdef123456"
    assert serialized["file_size"] == 1024


def test_update_info_properties_and_asset_resolution():
    asset_win = PlatformAsset("windows", "setup.msi", "https://example.com/win.msi", "hash1", 5000)
    asset_lin = PlatformAsset("linux", "setup.deb", "https://example.com/lin.deb", "hash2", 4000)

    info = UpdateInfo(
        available=True,
        current_version="1.0.0",
        latest_version="1.1.0",
        update_type="critical",
        assets={"windows": asset_win, "linux": asset_lin}
    )
    assert info.is_critical is True

    # Exact match
    assert info.get_platform_asset("windows") == asset_win
    assert info.get_platform_asset("linux") == asset_lin

    # Alias match
    info_alias = UpdateInfo(
        available=True,
        current_version="1.0.0",
        latest_version="1.1.0",
        assets={"win64": asset_win, "deb": asset_lin}
    )
    assert info_alias.get_platform_asset("windows") == asset_win
    assert info_alias.get_platform_asset("linux") == asset_lin

    # Extension match fallback
    asset_ext_msi = PlatformAsset("custom", "app_build.msi", "https://example.com/app.msi")
    info_ext = UpdateInfo(
        available=True,
        current_version="1.0.0",
        latest_version="1.1.0",
        assets={"other": asset_ext_msi}
    )
    assert info_ext.get_platform_asset("windows") == asset_ext_msi

    # Fallback to direct download_url if no asset map
    info_direct = UpdateInfo(
        available=True,
        current_version="1.0.0",
        latest_version="1.1.0",
        download_url="https://example.com/downloads/package.zip",
        sha256="directhash",
        file_size=999
    )
    resolved_direct = info_direct.get_platform_asset("freebsd")
    assert resolved_direct is not None
    assert resolved_direct.filename == "package.zip"
    assert resolved_direct.sha256 == "directhash"

    # None if nothing matches and no download_url
    info_empty = UpdateInfo(available=True, current_version="1.0.0", latest_version="1.1.0")
    assert info_empty.get_platform_asset("solaris") is None

    # Auto OS detection from sys.platform
    with patch("sys.platform", "win32"):
        assert info.get_platform_asset() == asset_win
    with patch("sys.platform", "linux"):
        assert info.get_platform_asset() == asset_lin
    with patch("sys.platform", "darwin"):
        assert info.get_platform_asset() is None
    with patch("sys.platform", "unknown_os"):
        assert info.get_platform_asset() is None


# ==========================================
# 2. ManifestFetcher Tests
# ==========================================

def test_manifest_fetcher_no_url():
    fetcher = ManifestFetcher()
    assert fetcher.fetch_manifest() is None


def test_manifest_fetcher_success():
    fetcher = ManifestFetcher("https://example.com/version.json")
    mock_payload = {
        "version": "1.2.0",
        "update_type": "feature",
        "changelog": "Lots of fixes"
    }
    json_bytes = json.dumps(mock_payload).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json_bytes
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = fetcher.fetch_manifest()
        assert res is not None
        assert res["latest_version"] == "1.2.0"
        assert res["changelog"] == "Lots of fixes"


def test_manifest_fetcher_http_and_network_errors():
    fetcher = ManifestFetcher("https://example.com/version.json")

    # Non-200 status
    mock_resp = MagicMock()
    mock_resp.status = 500
    mock_resp.__enter__.return_value = mock_resp
    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert fetcher.fetch_manifest() is None

    # HTTPError
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("url", 404, "Not Found", {}, None)):
        assert fetcher.fetch_manifest() is None

    # URLError
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        assert fetcher.fetch_manifest() is None

    # Bad JSON
    mock_resp2 = MagicMock()
    mock_resp2.status = 200
    mock_resp2.read.return_value = b"{ invalid json"
    mock_resp2.__enter__.return_value = mock_resp2
    with patch("urllib.request.urlopen", return_value=mock_resp2):
        assert fetcher.fetch_manifest() is None

    # General exception
    with patch("urllib.request.urlopen", side_effect=RuntimeError("Unexpected")):
        assert fetcher.fetch_manifest() is None


def test_manifest_normalize_github_release():
    gh_payload = {
        "tag_name": "v1.3.0",
        "body": "Detailed release notes",
        "published_at": "2026-09-22T12:00:00Z",
        "html_url": "https://github.com/org/repo/releases/v1.3.0",
        "assets": [
            {
                "name": "SQRT_Gem-1.3.0.msi",
                "browser_download_url": "https://github.com/org/repo/download/setup.msi",
                "size": 15000000
            },
            {
                "name": "sqrt-gem_1.3.0_amd64.deb",
                "browser_download_url": "https://github.com/org/repo/download/package.deb",
                "size": 14000000
            }
        ]
    }
    normalized = ManifestFetcher.normalize_manifest(gh_payload)
    assert normalized["latest_version"] == "1.3.0"
    assert normalized["release_date"] == "2026-09-22"
    assert "windows" in normalized["assets"]
    assert normalized["assets"]["windows"]["filename"] == "SQRT_Gem-1.3.0.msi"
    assert "linux" in normalized["assets"]
    assert normalized["assets"]["linux"]["filename"] == "sqrt-gem_1.3.0_amd64.deb"


# ==========================================
# 3. DownloadManager & calculate_sha256 Tests
# ==========================================

def test_calculate_sha256(tmp_path):
    test_file = tmp_path / "test.txt"
    content = b"Hello, SQRT_Gem updater verification!"
    test_file.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest().lower()
    assert calculate_sha256(test_file) == expected_hash


def test_download_manager_successful_download(tmp_path):
    manager = DownloadManager(download_dir=tmp_path)
    content = b"Mock installer payload content repeated " * 100
    expected_hash = hashlib.sha256(content).hexdigest().lower()

    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Length": str(len(content))}
    mock_resp.read.side_effect = [content[:500], content[500:], b""]
    mock_resp.__enter__.return_value = mock_resp

    progress_records = []
    def on_progress(bytes_read, total_bytes, percent, speed):
        progress_records.append((bytes_read, total_bytes, percent))

    with patch("urllib.request.urlopen", return_value=mock_resp):
        out_path = manager.download(
            url="https://example.com/setup.msi",
            expected_sha256=expected_hash,
            target_filename="setup.msi",
            progress_callback=on_progress
        )

    assert out_path.exists()
    assert out_path.name == "setup.msi"
    assert out_path.read_bytes() == content
    assert len(progress_records) > 0


def test_download_manager_checksum_mismatch(tmp_path):
    manager = DownloadManager(download_dir=tmp_path)
    content = b"Some valid content"

    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Length": str(len(content))}
    mock_resp.read.side_effect = [content, b""]
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(ChecksumMismatchError):
            manager.download(
                url="https://example.com/setup.msi",
                expected_sha256="wrong_checksum_hash",
                target_filename="setup.msi"
            )

    # Destination should not exist
    assert not (tmp_path / "setup.msi").exists()
    assert not (tmp_path / "setup.msi.part").exists()


def test_download_manager_cancelled(tmp_path):
    manager = DownloadManager(download_dir=tmp_path)

    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Length": "1000"}
    mock_resp.__enter__.return_value = mock_resp

    def fake_read(size):
        manager.cancel()
        return b"data chunk"

    mock_resp.read.side_effect = fake_read

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(DownloadCancelledError):
            manager.download(url="https://example.com/setup.msi")

    manager.reset_cancellation()
    assert manager._cancelled is False



def test_download_worker(tmp_path, qapp):
    manager = DownloadManager(download_dir=tmp_path)
    content = b"Worker binary file data"
    expected_hash = hashlib.sha256(content).hexdigest()

    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Length": str(len(content))}
    mock_resp.read.side_effect = [content, b""]
    mock_resp.__enter__.return_value = mock_resp

    worker = DownloadWorker(manager, "https://example.com/file.msi", expected_hash, "file.msi")
    finished_files = []
    errors = []

    worker.download_finished.connect(finished_files.append)
    worker.download_error.connect(errors.append)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        worker.run()

    assert len(finished_files) == 1
    assert Path(finished_files[0]).name == "file.msi"
    assert len(errors) == 0

    # Test error emission
    worker_fail = DownloadWorker(manager, "https://example.com/file.msi", "bad_hash", "fail.msi")
    fail_errors = []
    worker_fail.download_error.connect(fail_errors.append)

    mock_resp2 = MagicMock()
    mock_resp2.headers = {"Content-Length": str(len(content))}
    mock_resp2.read.side_effect = [content, b""]
    mock_resp2.__enter__.return_value = mock_resp2

    with patch("urllib.request.urlopen", return_value=mock_resp2):
        worker_fail.run()

    assert len(fail_errors) == 1


# ==========================================
# 4. InstallerRunner Tests
# ==========================================

def test_installer_runner_commands():
    msi_path = Path("C:/test/installer.msi")
    deb_path = Path("/tmp/installer.deb")

    with patch("sys.platform", "win32"):
        cmd_passive = InstallerRunner.get_install_command(msi_path, passive=True)
        assert cmd_passive[0] == "msiexec.exe"
        assert "/passive" in cmd_passive

        cmd_interactive = InstallerRunner.get_install_command(msi_path, passive=False)
        assert "/i" in cmd_interactive

        exe_path = Path("C:/test/installer.exe")
        assert InstallerRunner.get_install_command(exe_path) == [str(exe_path.resolve())]

    with patch("sys.platform", "linux"):
        cmd_deb = InstallerRunner.get_install_command(deb_path)
        assert cmd_deb == ["pkexec", "dpkg", "-i", str(deb_path.resolve())]

        sh_path = Path("/tmp/installer.sh")
        assert InstallerRunner.get_install_command(sh_path) == ["chmod", "+x", str(sh_path.resolve()), "&&", str(sh_path.resolve())]

    with patch("sys.platform", "darwin"):
        dmg_path = Path("/tmp/installer.dmg")
        assert InstallerRunner.get_install_command(dmg_path) == ["open", str(dmg_path.resolve())]


def test_installer_runner_launch(tmp_path):
    installer_file = tmp_path / "package.msi"
    installer_file.write_text("dummy")

    # Nonexistent file fails
    assert InstallerRunner.launch(tmp_path / "nonexistent.msi") is False

    # Successful launch with win32
    with patch("sys.platform", "win32"):
        with patch("subprocess.Popen") as mock_popen:
            with patch("PySide6.QtWidgets.QApplication.instance") as mock_app:
                app_obj = MagicMock()
                mock_app.return_value = app_obj

                success = InstallerRunner.launch(installer_file, passive=True, quit_app=True)
                assert success is True
                assert mock_popen.called
                assert app_obj.quit.called

    # Successful launch with linux
    with patch("sys.platform", "linux"):
        with patch("subprocess.Popen") as mock_popen:
            success = InstallerRunner.launch(installer_file, quit_app=False)
            assert success is True
            assert mock_popen.called


# ==========================================
# 5. UpdateChecker Network & Asset Resolution
# ==========================================

def test_update_checker_network_fetch():
    checker = UpdateChecker(current_version="1.0.0", manifest_url="https://example.com/manifest.json")
    mock_manifest = {
        "latest_version": "1.2.0",
        "min_supported_version": "1.0.0",
        "update_type": "feature",
        "assets": {
            "windows": {
                "platform": "windows",
                "filename": "update.msi",
                "download_url": "https://example.com/update.msi",
                "sha256": "abcdef",
                "file_size": 2048
            }
        }
    }

    with patch.object(checker.manifest_fetcher, "fetch_manifest", return_value=mock_manifest):
        with patch("sys.platform", "win32"):
            info = checker.check_for_updates(fetch_network=True)
            assert info.available is True
            assert info.latest_version == "1.2.0"
            assert info.download_url == "https://example.com/update.msi"
            assert info.sha256 == "abcdef"
            assert info.file_size == 2048


def test_update_checker_offline_returns_not_available():
    checker = UpdateChecker(current_version="1.0.0")
    with patch.object(checker.manifest_fetcher, "fetch_manifest", return_value=None):
        info = checker.check_for_updates(manifest_data=None, fetch_network=True)
        assert info.available is False
        assert info.current_version == "1.0.0"
        assert info.latest_version == "1.0.0"

