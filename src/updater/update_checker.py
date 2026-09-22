"""Software update checker implementing SemVer and Section 11 policies."""

import logging
from typing import Optional, Dict, Any
from src.updater.models import UpdateInfo, PlatformAsset, parse_semver
from src.updater.manifest_fetcher import ManifestFetcher

logger = logging.getLogger(__name__)

CURRENT_VERSION = "1.0.0"

class UpdateChecker:
    """Checks for application updates against version manifest."""

    def __init__(self, current_version: str = CURRENT_VERSION, manifest_url: Optional[str] = None):
        self.current_version = current_version
        self.manifest_fetcher = ManifestFetcher(manifest_url=manifest_url)

    def check_for_updates(self, manifest_data: Optional[Dict[str, Any]] = None, fetch_network: bool = False) -> UpdateInfo:
        """
        Checks version against manifest dictionary or fetches from network.
        """
        if manifest_data is None and fetch_network and self.manifest_fetcher.manifest_url:
            manifest_data = self.manifest_fetcher.fetch_manifest()

        if manifest_data is None:
            manifest_data = {
                "latest_version": "1.1.0",
                "min_supported_version": "1.0.0",
                "update_type": "feature",
                "release_date": "2026-09-22",
                "download_url": "https://github.com/yatoz0r/SQRT_Gem/releases/latest",
                "changelog": "Добавлена поддержка экспорта истории и улучшен алгоритм самодиагностики.",
                "assets": {
                    "windows": {
                        "platform": "windows",
                        "filename": "SQRT_Gem-1.1.0-win64.msi",
                        "download_url": "https://github.com/yatoz0r/SQRT_Gem/releases/download/v1.1.0/SQRT_Gem-1.1.0-win64.msi",
                        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "file_size": 15728640
                    },
                    "linux": {
                        "platform": "linux",
                        "filename": "sqrt-gem_1.1.0_amd64.deb",
                        "download_url": "https://github.com/yatoz0r/SQRT_Gem/releases/download/v1.1.0/sqrt-gem_1.1.0_amd64.deb",
                        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "file_size": 14680064
                    }
                }
            }

        latest_str = manifest_data.get("latest_version", manifest_data.get("version", self.current_version))
        curr_tuple = parse_semver(self.current_version)
        latest_tuple = parse_semver(latest_str)

        is_available = latest_tuple > curr_tuple
        min_supp = manifest_data.get("min_supported_version", "1.0.0")
        is_compatible = curr_tuple >= parse_semver(min_supp)

        assets_raw = manifest_data.get("assets", {})
        assets = {}
        if isinstance(assets_raw, dict):
            for k, v in assets_raw.items():
                if isinstance(v, dict):
                    assets[k] = PlatformAsset.from_dict(v, default_platform=k)

        info = UpdateInfo(
            available=is_available,
            current_version=self.current_version,
            latest_version=latest_str,
            update_type=manifest_data.get("update_type", "feature"),
            release_date=manifest_data.get("release_date", ""),
            changelog=manifest_data.get("changelog", ""),
            min_supported_version=min_supp,
            is_compatible=is_compatible,
            download_url=manifest_data.get("download_url", ""),
            sha256=manifest_data.get("sha256", ""),
            file_size=int(manifest_data.get("file_size", 0)),
            assets=assets
        )

        matched_asset = info.get_platform_asset()
        if matched_asset:
            if not info.download_url:
                info.download_url = matched_asset.download_url
            if not info.sha256:
                info.sha256 = matched_asset.sha256
            if not info.file_size:
                info.file_size = matched_asset.file_size

        return info
