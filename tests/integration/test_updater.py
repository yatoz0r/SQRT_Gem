"""Integration tests for update checking and version compatibility."""

from src.updater import UpdateChecker, UpdateInfo

def test_updater_newer_version_available():
    checker = UpdateChecker(current_version="1.0.0")
    manifest = {
        "latest_version": "1.1.0",
        "min_supported_version": "1.0.0",
        "update_type": "feature",
        "download_url": "https://example.com/v1.1.0",
        "changelog": "New features added"
    }
    info = checker.check_for_updates(manifest)
    assert info.available is True
    assert info.latest_version == "1.1.0"
    assert info.update_type == "feature"
    assert info.is_compatible is True

def test_updater_critical_patch():
    checker = UpdateChecker(current_version="1.0.0")
    manifest = {
        "latest_version": "1.0.1",
        "min_supported_version": "1.0.0",
        "update_type": "critical",
        "download_url": "https://example.com/v1.0.1",
        "changelog": "Critical security fix"
    }
    info = checker.check_for_updates(manifest)
    assert info.available is True
    assert info.update_type == "critical"

def test_updater_already_on_latest():
    checker = UpdateChecker(current_version="2.0.0")
    manifest = {
        "latest_version": "1.5.0",
        "min_supported_version": "1.0.0"
    }
    info = checker.check_for_updates(manifest)
    assert info.available is False
