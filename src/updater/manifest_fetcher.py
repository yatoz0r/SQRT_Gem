"""Fetches and normalizes version manifests from remote servers or GitHub Releases."""

import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5.0
DEFAULT_USER_AGENT = "SQRT_Gem-Updater/1.0 (Desktop; Python)"

class ManifestFetcher:
    """Handles network retrieval of update metadata manifests."""

    def __init__(self, manifest_url: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        self.manifest_url = manifest_url
        self.timeout = timeout

    def fetch_manifest(self, url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches manifest from remote URL (raw JSON or GitHub API).
        Returns normalized dictionary or None if fetch failed.
        """
        target_url = url or self.manifest_url
        if not target_url:
            return None

        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "application/json, text/plain, */*"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status not in (200, 201):
                    logger.warning(f"Manifest fetch returned HTTP status {response.status}")
                    return None
                data_bytes = response.read()
                raw_text = data_bytes.decode("utf-8")
                parsed = json.loads(raw_text)
                return self.normalize_manifest(parsed)
        except urllib.error.HTTPError as e:
            logger.warning(f"HTTP error fetching update manifest: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.warning(f"Network error fetching update manifest: {e.reason}")
            return None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse update manifest JSON: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error fetching update manifest: {e}")
            return None

    @staticmethod
    def normalize_manifest(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes both custom version.json manifests and GitHub Release API payloads.
        """
        if "tag_name" in data and ("assets" in data or "body" in data):
            version_str = data.get("tag_name", "").lstrip("v")
            changelog = data.get("body", "")
            release_date = data.get("published_at", "")[:10]
            
            assets_dict = {}
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                download_url = asset.get("browser_download_url", "")
                size = asset.get("size", 0)
                if name.endswith(".msi") or name.endswith(".exe"):
                    assets_dict["windows"] = {
                        "platform": "windows",
                        "filename": name,
                        "download_url": download_url,
                        "file_size": size,
                        "sha256": ""
                    }
                elif name.endswith(".deb") or name.endswith(".AppImage"):
                    assets_dict["linux"] = {
                        "platform": "linux",
                        "filename": name,
                        "download_url": download_url,
                        "file_size": size,
                        "sha256": ""
                    }

            return {
                "latest_version": version_str,
                "min_supported_version": "1.0.0",
                "update_type": "feature",
                "release_date": release_date,
                "changelog": changelog,
                "download_url": data.get("html_url", ""),
                "assets": assets_dict
            }

        normalized = dict(data)
        if "version" in normalized and "latest_version" not in normalized:
            normalized["latest_version"] = normalized["version"]
        return normalized
