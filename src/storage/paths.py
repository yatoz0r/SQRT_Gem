"""Cross-platform directory and file path management for user data and configurations."""

import os
import sys
from pathlib import Path

APP_NAME = "SQRT_Gem"

def get_app_data_dir() -> Path:
    """
    Returns the platform-specific directory where application user data is stored.
    Windows: %APPDATA%/SQRT_Gem
    Linux/macOS: ~/.config/sqrt_gem
    """
    if sys.platform == "win32":
        app_data = os.getenv("APPDATA")
        if app_data:
            base_dir = Path(app_data)
        else:
            base_dir = Path.home() / "AppData" / "Roaming"
        data_dir = base_dir / APP_NAME
    else:
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            base_dir = Path(xdg_config)
        else:
            base_dir = Path.home() / ".config"
        data_dir = base_dir / APP_NAME.lower()

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_config_file_path() -> Path:
    """Returns the absolute path to config.json."""
    return get_app_data_dir() / "config.json"

def get_history_file_path() -> Path:
    """Returns the absolute path to history.json."""
    return get_app_data_dir() / "history.json"

def get_logs_dir() -> Path:
    """Returns the logs directory path."""
    logs_dir = get_app_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_locales_dir() -> Path:
    """Returns the directory containing locale JSON files."""
    # Check if running as packaged binary or source directory
    base_dir = Path(__file__).resolve().parent.parent.parent
    local_locales = base_dir / "locales"
    if local_locales.exists():
        return local_locales
    # Fallback to local directory
    return Path("locales").resolve()
