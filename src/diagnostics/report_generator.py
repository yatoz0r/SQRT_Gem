"""Diagnostic report and support bundle generator."""

import json
import time
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Optional
from src.diagnostics.health_checker import HealthChecker, HealthReport
from src.storage.paths import get_app_data_dir, get_config_file_path, get_history_file_path

class ReportGenerator:
    """Generates a comprehensive, sanitized diagnostic bundle (.zip) for technical support."""

    def __init__(self):
        self.health_checker = HealthChecker()

    def generate_support_bundle(self, output_dir: Optional[Path] = None) -> Path:
        target_dir = output_dir or (get_app_data_dir() / "diagnostic_reports")
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        zip_path = target_dir / f"support_bundle_{timestamp_str}.zip"

        # 1. Run health checks
        report: HealthReport = self.health_checker.run_all_checks()

        # 2. Read config (sanitized)
        cfg_path = get_config_file_path()
        sanitized_config = {}
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    sanitized_config = json.load(f)
            except Exception as e:
                sanitized_config = {"error": f"Failed to parse config: {e}"}

        # 3. Read history metadata (record count only, privacy-friendly)
        hist_path = get_history_file_path()
        history_meta = {"count": 0}
        if hist_path.exists():
            try:
                with open(hist_path, "r", encoding="utf-8") as f:
                    hdata = json.load(f)
                    records = hdata.get("records", []) if isinstance(hdata, dict) else hdata
                    history_meta = {
                        "count": len(records),
                        "schema_version": hdata.get("schema_version", "1.0.0") if isinstance(hdata, dict) else "unknown"
                    }
            except Exception as e:
                history_meta = {"error": str(e)}

        # 4. Create ZIP bundle
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # Add health report
            report_dict = {
                "overall_status": report.overall_status,
                "os_info": report.os_info,
                "timestamp": report.timestamp,
                "checks": [asdict(c) for c in report.checks]
            }
            zf.writestr("health_report.json", json.dumps(report_dict, indent=2, ensure_ascii=False))
            zf.writestr("sanitized_config.json", json.dumps(sanitized_config, indent=2, ensure_ascii=False))
            zf.writestr("history_meta.json", json.dumps(history_meta, indent=2, ensure_ascii=False))

            # Diagnostic summary text
            summary_lines = [
                "===========================================================",
                "             SQRT_Gem Diagnostic Support Report            ",
                "===========================================================",
                f"Generated: {time.ctime()}",
                f"Status:    {report.overall_status}",
                f"Platform:  {report.os_info.get('platform')}",
                f"Python:    {report.os_info.get('python_version')}",
                "-----------------------------------------------------------",
                "Check Results:"
            ]
            for c in report.checks:
                summary_lines.append(f"  [{c.status:4}] {c.name}: {c.detail} ({c.duration_ms} ms)")
            summary_lines.append("===========================================================")
            zf.writestr("summary.txt", "\n".join(summary_lines))

        return zip_path
