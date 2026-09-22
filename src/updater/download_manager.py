"""Download manager with streaming progress tracking, SHA-256 integrity verification, and Qt Signals."""

import hashlib
import logging
import os
import shutil
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Callable, Optional
from PySide6.QtCore import QObject, Signal
from src.storage.paths import get_app_data_dir

logger = logging.getLogger(__name__)

CHUNK_SIZE = 64 * 1024  # 64 KB chunks

class ChecksumMismatchError(Exception):
    """Raised when downloaded file sha256 does not match expected hash."""
    pass

class DownloadCancelledError(Exception):
    """Raised when download was intentionally cancelled."""
    pass

def calculate_sha256(file_path: Path) -> str:
    """Calculates SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest().lower()

class DownloadManager:
    """Core download logic with chunked reading and SHA-256 verification."""

    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or (get_app_data_dir() / "updates")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self._cancelled = False

    def cancel(self):
        """Signals current download to abort."""
        self._cancelled = True

    def reset_cancellation(self):
        self._cancelled = False

    def download(
        self,
        url: str,
        expected_sha256: str = "",
        target_filename: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, float, float], None]] = None
    ) -> Path:
        """
        Downloads file from url to target destination.
        """
        self._cancelled = False
        if not target_filename:
            target_filename = url.split("/")[-1].split("?")[0] or "update_package.bin"

        dest_path = self.download_dir / target_filename
        temp_path = self.download_dir / f"{target_filename}.part"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SQRT_Gem-Updater/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                total_bytes = int(resp.headers.get("Content-Length", 0))
                bytes_read = 0
                hasher = hashlib.sha256()
                start_time = time.time()
                last_time = start_time
                bytes_since_last = 0
                current_speed = 0.0

                with open(temp_path, "wb") as f:
                    while True:
                        if self._cancelled:
                            raise DownloadCancelledError("Download cancelled by user")
                        
                        chunk = resp.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        hasher.update(chunk)
                        chunk_len = len(chunk)
                        bytes_read += chunk_len
                        bytes_since_last += chunk_len

                        now = time.time()
                        time_diff = now - last_time
                        if time_diff >= 0.2:
                            current_speed = bytes_since_last / time_diff
                            last_time = now
                            bytes_since_last = 0

                            if progress_callback:
                                percent = (bytes_read / total_bytes * 100.0) if total_bytes > 0 else 0.0
                                progress_callback(bytes_read, total_bytes, percent, current_speed)

                if progress_callback:
                    percent = 100.0 if total_bytes > 0 else 0.0
                    progress_callback(bytes_read, total_bytes, percent, current_speed)

            computed_hash = hasher.hexdigest().lower()
            if expected_sha256:
                expected_clean = expected_sha256.lower().strip()
                if computed_hash != expected_clean:
                    if temp_path.exists():
                        temp_path.unlink()
                    raise ChecksumMismatchError(
                        f"Checksum mismatch: expected {expected_clean}, got {computed_hash}"
                    )

            if dest_path.exists():
                dest_path.unlink()
            shutil.move(temp_path, dest_path)
            return dest_path

        except Exception:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise

class DownloadWorker(QObject):
    """PySide6 Worker object for running download inside a QThread."""

    progress_updated = Signal(int, int, float, float)  # bytes_read, total_bytes, percent, speed_bps
    download_finished = Signal(str)                   # file_path
    download_error = Signal(str)                      # error message
    download_cancelled = Signal()

    def __init__(self, manager: DownloadManager, url: str, expected_sha256: str = "", filename: Optional[str] = None):
        super().__init__()
        self.manager = manager
        self.url = url
        self.expected_sha256 = expected_sha256
        self.filename = filename

    def run(self):
        """Entry point executed in background QThread."""
        try:
            dest_file = self.manager.download(
                url=self.url,
                expected_sha256=self.expected_sha256,
                target_filename=self.filename,
                progress_callback=self._on_progress
            )
            self.download_finished.emit(str(dest_file))
        except DownloadCancelledError:
            self.download_cancelled.emit()
        except ChecksumMismatchError as e:
            self.download_error.emit(str(e))
        except Exception as e:
            logger.error(f"Download failed: {e}", exc_info=True)
            self.download_error.emit(str(e))

    def _on_progress(self, bytes_read: int, total_bytes: int, percent: float, speed_bps: float):
        self.progress_updated.emit(bytes_read, total_bytes, percent, speed_bps)
