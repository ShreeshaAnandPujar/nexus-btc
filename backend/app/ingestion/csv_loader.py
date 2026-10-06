"""High-throughput CSV/TSV transaction loader."""

import csv
import io
from pathlib import Path
from typing import Generator, Any
from app.ingestion.normalizer import normalize_raw_record


class CsvLoader:
    """Robust CSV loader that processes rows one by one without loading whole file into memory."""

    @staticmethod
    def parse_content(
        content: str | bytes, source_file: str = "upload.csv"
    ) -> Generator[tuple[dict[str, Any], list[str], str, int], None, None]:
        """
        Stream parsed rows from CSV text/bytes.
        Yields: (canonical_dict, quality_flags, validation_status, row_number)
        """
        text = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else content
        reader = csv.DictReader(io.StringIO(text))

        for row_idx, row in enumerate(reader, start=2):  # row 1 is header
            try:
                canonical, flags, status = normalize_raw_record(row, source_file, row_idx)
                yield canonical, flags, status, row_idx
            except Exception as e:
                # Malformed row fallback
                yield {"raw": row, "error": str(e)}, ["FLAG_ROW_CORRUPT"], "INVALID", row_idx

    @classmethod
    def parse_file(
        cls, file_path: Path
    ) -> Generator[tuple[dict[str, Any], list[str], str, int], None, None]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):
                try:
                    canonical, flags, status = normalize_raw_record(row, str(file_path), row_idx)
                    yield canonical, flags, status, row_idx
                except Exception as e:
                    yield {"raw": row, "error": str(e)}, ["FLAG_ROW_CORRUPT"], "INVALID", row_idx
