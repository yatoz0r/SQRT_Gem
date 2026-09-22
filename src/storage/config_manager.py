"""Configuration manager with schema validation, atomic file operations, and self-recovery."""

import json
import logging
import os
import shutil
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Any, Optional
from src.storage.paths import get_config_file_path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.0.0",
    "language": "ru",
    "theme": "system",
    "default_precision": 50,
    "max_precision_limit": 1000,
    "auto_check_updates": True,
    "history_max_records": 500
}

@dataclass
class AppConfig:
    version: str = "1.0.0"
    language: str = "ru"
    theme: str = "system"
    default_precision: int = 50
    max_precision_limit: int = 1000
    auto_check_updates: bool = True
    history_max_records: int = 500
    was_corrupted_and_recovered: bool = False

class ConfigManager:
    """Manages application configuration loading, saving, and corruption recovery."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or get_config_file_path()
        self.config: AppConfig = self.load_config()

    def load_config(self) -> AppConfig:
        """Loads configuration from file. Automatically recovers if corrupted."""
        if not self.config_path.exists():
            cfg = AppConfig()
            self.save_config(cfg)
            return cfg

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Config root must be a dictionary")

            # Validate and extract settings with fallbacks
            return AppConfig(
                version=str(data.get("version", DEFAULT_CONFIG["version"])),
                language=str(data.get("language", DEFAULT_CONFIG["language"])),
                theme=str(data.get("theme", DEFAULT_CONFIG["theme"])),
                default_precision=int(data.get("default_precision", DEFAULT_CONFIG["default_precision"])),
                max_precision_limit=int(data.get("max_precision_limit", DEFAULT_CONFIG["max_precision_limit"])),
                auto_check_updates=bool(data.get("auto_check_updates", DEFAULT_CONFIG["auto_check_updates"])),
                history_max_records=int(data.get("history_max_records", DEFAULT_CONFIG["history_max_records"])),
                was_corrupted_and_recovered=False
            )

        except Exception as e:
            logger.warning(f"Configuration corrupted ({e}), performing self-recovery...")
            # Backup corrupted file
            corrupt_backup = self.config_path.with_name(f"config.corrupted.{int(time.time())}.json")
            try:
                shutil.copy2(self.config_path, corrupt_backup)
            except Exception as backup_err:
                logger.error(f"Failed to backup corrupted config: {backup_err}")

            # Recreate default
            recovered_config = AppConfig(was_corrupted_and_recovered=True)
            self.save_config(recovered_config)
            return recovered_config

    def save_config(self, config: Optional[AppConfig] = None) -> None:
        """Atomically saves configuration to disk."""
        if config is not None:
            self.config = config

        data = {
            "version": self.config.version,
            "language": self.config.language,
            "theme": self.config.theme,
            "default_precision": self.config.default_precision,
            "max_precision_limit": self.config.max_precision_limit,
            "auto_check_updates": self.config.auto_check_updates,
            "history_max_records": self.config.history_max_records
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.config_path.with_name(f"{self.config_path.name}.tmp.{os.getpid()}")

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_file, self.config_path)
        except Exception as e:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            raise OSError(f"Failed to atomically save configuration: {e}") from e

    def reset_to_defaults(self) -> AppConfig:
        """Resets configuration to factory defaults (Self-Service Recovery)."""
        self.config = AppConfig()
        self.save_config(self.config)
        return self.config
