"""Integration tests for the diagnostics and self-recovery service."""

import zipfile
from src.diagnostics import HealthChecker, ReportGenerator, RecoveryManager, get_faq_items
from src.storage import ConfigManager

def test_health_checker_run():
    checker = HealthChecker()
    report = checker.run_all_checks()
    assert report.overall_status in ["HEALTHY", "WARNING"]
    assert len(report.checks) >= 4

    # Check math benchmark inside health report
    bench = next(c for c in report.checks if "Benchmark" in c.name)
    assert bench.status == "PASS"

def test_report_generator_bundle(temp_dir):
    gen = ReportGenerator()
    zip_path = gen.generate_support_bundle(output_dir=temp_dir)
    assert zip_path.exists()
    assert zipfile.is_zipfile(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "health_report.json" in names
        assert "sanitized_config.json" in names
        assert "summary.txt" in names

def test_recovery_manager_factory_reset(temp_dir):
    cfg_file = temp_dir / "config.json"
    mgr = ConfigManager(config_path=cfg_file)
    mgr.config.language = "zh"
    mgr.config.default_precision = 999
    mgr.save_config()

    rm = RecoveryManager(config_manager=mgr)
    restored = rm.perform_factory_reset()
    assert restored.language == "ru"
    assert restored.default_precision == 50

def test_faq_items_available():
    items = get_faq_items()
    assert len(items) >= 4
