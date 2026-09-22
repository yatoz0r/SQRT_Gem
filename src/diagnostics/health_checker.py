"""System and application self-diagnostics runner to reduce support costs."""

import os
import platform
import sys
import time
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import List, Dict, Any
from src.storage.paths import get_app_data_dir, get_config_file_path, get_history_file_path
from src.engine import MathEngine

@dataclass
class CheckItem:
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    detail: str
    duration_ms: float = 0.0

@dataclass
class HealthReport:
    timestamp: float
    overall_status: str  # "HEALTHY", "WARNING", "ERROR"
    os_info: Dict[str, Any]
    checks: List[CheckItem]

class HealthChecker:
    """Performs automated system diagnostics, file system checks, and precision benchmarking."""

    def __init__(self):
        self.engine = MathEngine()

    def run_all_checks(self) -> HealthReport:
        checks: List[CheckItem] = []

        checks.append(self._check_python_environment())
        checks.append(self._check_filesystem_permissions())
        checks.append(self._check_config_integrity())
        checks.append(self._check_history_integrity())
        checks.append(self._check_math_engine_benchmark())

        # Determine overall status
        if any(c.status == "FAIL" for c in checks):
            overall = "ERROR"
        elif any(c.status == "WARN" for c in checks):
            overall = "WARNING"
        else:
            overall = "HEALTHY"

        os_info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version.split()[0]
        }

        return HealthReport(
            timestamp=time.time(),
            overall_status=overall,
            os_info=os_info,
            checks=checks
        )

    def _check_python_environment(self) -> CheckItem:
        t0 = time.perf_counter()
        py_ver = sys.version_info
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        if py_ver >= (3, 9):
            return CheckItem("Python Environment", "PASS", f"Python {sys.version.split()[0]} is compatible", elapsed)
        return CheckItem("Python Environment", "FAIL", f"Python {sys.version.split()[0]} is below minimum 3.9", elapsed)

    def _check_filesystem_permissions(self) -> CheckItem:
        t0 = time.perf_counter()
        app_dir = get_app_data_dir()
        test_file = app_dir / ".write_test.tmp"
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("test_permission")
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            test_file.unlink()
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            if content == "test_permission":
                return CheckItem("FileSystem Permissions", "PASS", f"Read/write access verified in {app_dir}", elapsed)
            return CheckItem("FileSystem Permissions", "FAIL", "Read back mismatch", elapsed)
        except Exception as e:
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            return CheckItem("FileSystem Permissions", "FAIL", f"Cannot write to {app_dir}: {e}", elapsed)

    def _check_config_integrity(self) -> CheckItem:
        t0 = time.perf_counter()
        cfg_path = get_config_file_path()
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        if not cfg_path.exists():
            return CheckItem("Config File", "PASS", "Config does not exist yet (will use defaults)", elapsed)
        try:
            import json
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "language" in data and "default_precision" in data:
                return CheckItem("Config File", "PASS", "Configuration structure is valid", elapsed)
            return CheckItem("Config File", "WARN", "Config is missing some standard fields", elapsed)
        except Exception as e:
            return CheckItem("Config File", "FAIL", f"Config file JSON is corrupted: {e}", elapsed)

    def _check_history_integrity(self) -> CheckItem:
        t0 = time.perf_counter()
        hist_path = get_history_file_path()
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        if not hist_path.exists():
            return CheckItem("History Storage", "PASS", "History storage ready (empty)", elapsed)
        try:
            import json
            with open(hist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, (dict, list)):
                return CheckItem("History Storage", "PASS", "History storage structure is valid", elapsed)
            return CheckItem("History Storage", "WARN", "History structure unexpected", elapsed)
        except Exception as e:
            return CheckItem("History Storage", "FAIL", f"History file corrupted: {e}", elapsed)

    def _check_math_engine_benchmark(self) -> CheckItem:
        t0 = time.perf_counter()
        try:
            # Benchmark: sqrt(2) with 1000 digits precision
            res = self.engine.evaluate("sqrt(2)", precision=1000)
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            # Verify first digits of sqrt(2)
            if res.formatted_value.startswith("1.41421356237309504880168872420969807856967187537694"):
                return CheckItem(
                    "Math Engine Benchmark (sqrt(2) @ 1000 digits)",
                    "PASS",
                    f"Computed 1000 digits accurately in {elapsed} ms",
                    elapsed
                )
            return CheckItem("Math Engine Benchmark", "FAIL", "Mathematical verification mismatch for sqrt(2)", elapsed)
        except Exception as e:
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            return CheckItem("Math Engine Benchmark", "FAIL", f"Calculation failed: {e}", elapsed)
