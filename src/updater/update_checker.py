"""Software update checker implementing SemVer and Section 11 policies."""

import json
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

CURRENT_VERSION = "1.0.0"

@dataclass
class UpdateInfo:
    available: bool
    current_version: str
    latest_version: str
    update_type: str  # "critical" or "feature"
    download_url: str
    changelog: str
    is_compatible: bool

def parse_semver(v: str) -> tuple:
    clean = v.strip().lstrip('v')
    parts = clean.split('.')
    try:
        return tuple(int(p) for p in parts[:3])
    except ValueError:
        return (0, 0, 0)

class UpdateChecker:
    """Checks for application updates against version manifest."""

    def __init__(self, current_version: str = CURRENT_VERSION):
        self.current_version = current_version

    def check_for_updates(self, manifest_data: Optional[Dict[str, Any]] = None) -> UpdateInfo:
        """
        Checks version against manifest dictionary or default update server payload.
        """
        if manifest_data is None:
            # Default simulated release manifest for verification & testing
            manifest_data = {
                "latest_version": "1.1.0",
                "min_supported_version": "1.0.0",
                "update_type": "feature",
                "download_url": "https://github.com/example/SQRT_Gem/releases/latest",
                "changelog": "Добавлена поддержка экспорта истории и улучшен алгоритм самодиагностики."
            }

        latest_str = manifest_data.get("latest_version", self.current_version)
        curr_tuple = parse_semver(self.current_version)
        latest_tuple = parse_semver(latest_str)

        is_available = latest_tuple > curr_tuple
        min_supp = manifest_data.get("min_supported_version", "1.0.0")
        is_compatible = curr_tuple >= parse_semver(min_supp)

        return UpdateInfo(
            available=is_available,
            current_version=self.current_version,
            latest_version=latest_str,
            update_type=manifest_data.get("update_type", "feature"),
            download_url=manifest_data.get("download_url", ""),
            changelog=manifest_data.get("changelog", ""),
            is_compatible=is_compatible
        )
