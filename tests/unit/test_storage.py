"""Unit tests for configuration and history persistence."""

import json
from pathlib import Path
from src.storage import ConfigManager, HistoryManager, AppConfig

def test_config_lifecycle(temp_dir):
    cfg_file = temp_dir / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    assert mgr.config.language == "ru"

    mgr.config.language = "en"
    mgr.config.default_precision = 100
    mgr.save_config()

    # Re-read
    mgr2 = ConfigManager(config_path=cfg_file)
    assert mgr2.config.language == "en"
    assert mgr2.config.default_precision == 100

def test_config_self_recovery_on_corruption(temp_dir):
    cfg_file = temp_dir / "config.json"
    # Write garbage to config file
    with open(cfg_file, "w", encoding="utf-8") as f:
        f.write("{ INVALID JSON DATA !@#$%^&*() }")

    mgr = ConfigManager(config_path=cfg_file)
    assert mgr.config.was_corrupted_and_recovered is True
    assert mgr.config.language == "ru"
    assert mgr.config.default_precision == 50

    # Ensure valid config was restored
    with open(cfg_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == "1.0.0"

def test_history_lifecycle(temp_dir):
    hist_file = temp_dir / "history.json"
    hm = HistoryManager(history_path=hist_file)
    assert len(hm.get_records()) == 0

    rec = hm.add_record("sqrt(144)", 0, "12", 0.5)
    assert len(hm.get_records()) == 1
    assert hm.get_records()[0].expression == "sqrt(144)"

    # Export to CSV
    csv_file = temp_dir / "export.csv"
    hm.export_to_csv(csv_file)
    assert csv_file.exists()
    assert "sqrt(144)" in csv_file.read_text(encoding="utf-8-sig")

    # Export to JSON
    json_file = temp_dir / "export.json"
    hm.export_to_json(json_file)
    assert json_file.exists()

    # Delete record
    hm.delete_record(rec.id)
    assert len(hm.get_records()) == 0
