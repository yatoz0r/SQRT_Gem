"""History manager for calculations with persistence, atomic writes, and export features."""

import csv
import json
import logging
import os
import shutil
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from src.storage.paths import get_history_file_path

logger = logging.getLogger(__name__)

@dataclass
class HistoryRecord:
    id: str
    timestamp: str
    expression: str
    precision: int
    result: str
    execution_time_ms: float
    status: str = "success"

class HistoryManager:
    """Manages history records, persistence to history.json, and CSV/JSON export."""

    def __init__(self, history_path: Optional[Path] = None, max_records: int = 500):
        self.history_path = history_path or get_history_file_path()
        self.max_records = max_records
        self.records: List[HistoryRecord] = self._load()

    def _load(self) -> List[HistoryRecord]:
        if not self.history_path.exists():
            return []

        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "records" in data:
                raw_list = data["records"]
            elif isinstance(data, list):
                raw_list = data
            else:
                raw_list = []

            records = []
            for item in raw_list:
                if isinstance(item, dict) and "expression" in item and "result" in item:
                    records.append(HistoryRecord(
                        id=str(item.get("id", uuid.uuid4())),
                        timestamp=str(item.get("timestamp", datetime.now(timezone.utc).isoformat())),
                        expression=str(item.get("expression", "")),
                        precision=int(item.get("precision", 0)),
                        result=str(item.get("result", "")),
                        execution_time_ms=float(item.get("execution_time_ms", 0.0)),
                        status=str(item.get("status", "success"))
                    ))
            return records

        except Exception as e:
            logger.warning(f"History file corrupted ({e}), creating backup and reinitializing...")
            corrupt_backup = self.history_path.with_name(f"history.corrupted.{int(time.time())}.json")
            try:
                shutil.copy2(self.history_path, corrupt_backup)
            except Exception as err:
                logger.error(f"Failed to backup corrupted history: {err}")
            return []

    def _save(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "1.0.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "records": [asdict(r) for r in self.records]
        }

        temp_file = self.history_path.with_name(f"{self.history_path.name}.tmp.{os.getpid()}")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_file, self.history_path)
        except Exception as e:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            raise OSError(f"Failed to atomically save history: {e}") from e

    def add_record(self, expression: str, precision: int, result: str, execution_time_ms: float) -> HistoryRecord:
        """Adds a new calculation entry to history and saves to disk."""
        rec = HistoryRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            expression=expression,
            precision=precision,
            result=result,
            execution_time_ms=execution_time_ms,
            status="success"
        )
        self.records.insert(0, rec)
        if len(self.records) > self.max_records:
            self.records = self.records[:self.max_records]
        self._save()
        return rec

    def get_records(self) -> List[HistoryRecord]:
        """Returns all history records in reverse chronological order."""
        return list(self.records)

    def delete_record(self, record_id: str) -> bool:
        """Deletes a record by ID."""
        initial_len = len(self.records)
        self.records = [r for r in self.records if r.id != record_id]
        if len(self.records) != initial_len:
            self._save()
            return True
        return False

    def clear(self) -> None:
        """Clears all history records."""
        self.records.clear()
        self._save()

    def export_to_csv(self, export_path: Path) -> None:
        """Exports history records to a CSV file."""
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Timestamp", "Expression", "Precision", "Result", "ExecutionTimeMs", "Status"])
            for r in self.records:
                writer.writerow([r.id, r.timestamp, r.expression, r.precision, r.result, r.execution_time_ms, r.status])

    def export_to_json(self, export_path: Path) -> None:
        """Exports history records to a standalone JSON file."""
        export_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "records_count": len(self.records),
            "records": [asdict(r) for r in self.records]
        }
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
