"""End-to-end user flow test simulating complete calculation, settings, history, and diagnostics lifecycle."""

from pathlib import Path
from src.engine import MathEngine
from src.storage import ConfigManager, HistoryManager
from src.i18n import LocalizationService, tr
from src.diagnostics import HealthChecker, ReportGenerator, RecoveryManager

def test_complete_end_to_end_user_journey(temp_dir):
    # 1. Initialize system with isolated storage in temporary directory
    cfg_file = temp_dir / "user_config.json"
    hist_file = temp_dir / "user_history.json"

    config_mgr = ConfigManager(config_path=cfg_file)
    history_mgr = HistoryManager(history_path=hist_file)
    engine = MathEngine()
    i18n = LocalizationService()

    # 2. Change language to English
    i18n.set_language("en")
    config_mgr.config.language = "en"
    config_mgr.save_config()
    assert tr("btn_calculate") == "Calculate (=)"

    # 3. Perform basic calculation: sqrt(144)
    res1 = engine.evaluate("sqrt(144)", precision=2)
    assert res1.formatted_value == "12.00"
    history_mgr.add_record(res1.expression, res1.precision, res1.formatted_value, res1.elapsed_ms)

    # 4. Perform high-precision calculation with 500 digits
    res2 = engine.evaluate("sqrt(2)", precision=500)
    assert len(res2.formatted_value.split(".")[1]) == 500
    assert res2.formatted_value.startswith("1.41421356237309504880168872420969807856967187537694")
    history_mgr.add_record(res2.expression, res2.precision, res2.formatted_value, res2.elapsed_ms)

    # 5. Perform calculation with very long numbers (>1000 digits)
    long_num = "123456789012345678901234567890" * 35  # >1000 digits!
    res3 = engine.evaluate(f"({long_num} + 1) - {long_num}", precision=0)
    assert res3.formatted_value == "1"
    history_mgr.add_record("very_long_expression", 0, res3.formatted_value, res3.elapsed_ms)

    # 6. Verify history content
    records = history_mgr.get_records()
    assert len(records) == 3
    assert records[0].expression == "very_long_expression"
    assert records[2].expression == "sqrt(144)"

    # 7. Export history
    csv_export = temp_dir / "history_export.csv"
    history_mgr.export_to_csv(csv_export)
    assert csv_export.exists()
    assert "12.00" in csv_export.read_text(encoding="utf-8-sig")

    # 8. Run system diagnostics
    checker = HealthChecker()
    report = checker.run_all_checks()
    assert report.overall_status in ["HEALTHY", "WARNING"]

    # 9. Export support bundle
    reporter = ReportGenerator()
    bundle_path = reporter.generate_support_bundle(output_dir=temp_dir)
    assert bundle_path.exists()

    # 10. Perform factory reset and verify history remains intact
    recovery = RecoveryManager(config_manager=config_mgr)
    restored_cfg = recovery.perform_factory_reset()
    assert restored_cfg.language == "ru"

    # History is still present!
    history_after_reset = HistoryManager(history_path=hist_file)
    assert len(history_after_reset.get_records()) == 3
