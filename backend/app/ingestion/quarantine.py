"""Quarantine manager for malformed or unrecoverable transaction records."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.core.config import settings
from app.core.logging import logger


class QuarantineManager:
    """Safely saves unparseable or malicious records to quarantine storage."""

    def __init__(self, quarantine_dir: Path | None = None):
        self.quarantine_dir = quarantine_dir or settings.QUARANTINE_DIR
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def quarantine_record(
        self,
        raw_record: Any,
        source_file: str,
        source_row: int,
        error_reason: str,
        ingestion_id: str,
    ) -> Path:
        """Persist a single quarantined record to disk without crashing."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_source = Path(source_file).stem[:32]
        file_path = self.quarantine_dir / f"quarantine_{safe_source}_{timestamp}_{source_row}.json"

        payload = {
            "ingestion_id": ingestion_id,
            "source_file": source_file,
            "source_row": source_row,
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "error_reason": error_reason,
            "raw_payload": str(raw_record),
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            logger.warning(
                f"Quarantined malformed record at {source_file}:{source_row} -> {file_path.name}: {error_reason}"
            )
        except Exception as e:
            logger.error(f"Failed writing quarantine record: {e}")

        return file_path

    def get_quarantined_records(self, ingestion_id: str | None = None) -> list[dict]:
        """Retrieve quarantined records optionally filtered by ingestion_id."""
        results = []
        for p in self.quarantine_dir.glob("quarantine_*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if ingestion_id is None or data.get("ingestion_id") == ingestion_id:
                    results.append(data)
            except Exception:
                continue
        return results
