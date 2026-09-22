"""Shared pytest fixtures."""

import os
import tempfile
from pathlib import Path
import pytest
from src.engine import MathEngine
from src.storage import ConfigManager, HistoryManager
from src.i18n import LocalizationService
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)

@pytest.fixture
def math_engine():
    return MathEngine()

@pytest.fixture
def temp_config_manager(temp_dir):
    cfg_file = temp_dir / "test_config.json"
    return ConfigManager(config_path=cfg_file)

@pytest.fixture
def temp_history_manager(temp_dir):
    hist_file = temp_dir / "test_history.json"
    return HistoryManager(history_path=hist_file)

@pytest.fixture
def i18n_service():
    return LocalizationService()
