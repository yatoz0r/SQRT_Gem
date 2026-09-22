"""Data models for software updates, platform assets, and SemVer parsing."""

from dataclasses import dataclass, field
import re
import sys
from typing import Dict, Any, Optional, Tuple

def parse_semver(v: str) -> Tuple[int, int, int]:
    """
    Parses a SemVer version string into a (major, minor, patch) integer tuple.
    Handles 'v1.2.3', '1.2.3-beta', '1.2', etc.
    """
    if not v:
        return (0, 0, 0)
    clean = str(v).strip().lstrip('v')
    clean = re.split(r'[-+]', clean)[0]
    parts = clean.split('.')
    nums = []
    for p in parts[:3]:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2])

@dataclass
class PlatformAsset:
    """Represents a platform-specific release binary asset."""
    platform: str  # "windows", "linux", "macos", "any"
    filename: str
    download_url: str
    sha256: str = ""
    file_size: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any], default_platform: str = "any") -> "PlatformAsset":
        return cls(
            platform=data.get("platform", default_platform),
            filename=data.get("filename", ""),
            download_url=data.get("download_url", data.get("url", "")),
            sha256=data.get("sha256", data.get("hash", "")).lower().strip(),
            file_size=int(data.get("file_size", data.get("size", 0)))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "filename": self.filename,
            "download_url": self.download_url,
            "sha256": self.sha256,
            "file_size": self.file_size
        }

@dataclass
class UpdateInfo:
    """Detailed information about an available software update."""
    available: bool
    current_version: str
    latest_version: str
    update_type: str = "feature"  # "patch", "feature", "critical"
    release_date: str = ""
    changelog: str = ""
    min_supported_version: str = "1.0.0"
    is_compatible: bool = True
    download_url: str = ""
    sha256: str = ""
    file_size: int = 0
    assets: Dict[str, PlatformAsset] = field(default_factory=dict)

    @property
    def is_critical(self) -> bool:
        return self.update_type.lower() == "critical"

    def get_platform_asset(self, os_name: Optional[str] = None) -> Optional[PlatformAsset]:
        """
        Resolves the appropriate platform binary asset for the running OS.
        Checks for exact OS match, then extension match (.msi for Windows, .deb for Linux).
        """
        if not os_name:
            if sys.platform == "win32":
                os_name = "windows"
            elif sys.platform.startswith("linux"):
                os_name = "linux"
            elif sys.platform == "darwin":
                os_name = "macos"
            else:
                os_name = sys.platform

        os_name = os_name.lower()
        if os_name in self.assets:
            return self.assets[os_name]

        aliases = {
            "windows": ["win", "win64", "win32", "msi"],
            "linux": ["deb", "ubuntu", "debian", "tar.gz"],
            "macos": ["darwin", "mac", "dmg"]
        }
        for alias in aliases.get(os_name, []):
            if alias in self.assets:
                return self.assets[alias]

        ext_map = {
            "windows": ".msi",
            "linux": ".deb",
            "macos": ".dmg"
        }
        target_ext = ext_map.get(os_name, "")
        if target_ext:
            for asset in self.assets.values():
                if asset.filename.lower().endswith(target_ext):
                    return asset

        if self.download_url:
            filename = self.download_url.split("/")[-1].split("?")[0] or "update_installer"
            return PlatformAsset(
                platform=os_name,
                filename=filename,
                download_url=self.download_url,
                sha256=self.sha256,
                file_size=self.file_size
            )

        return None
