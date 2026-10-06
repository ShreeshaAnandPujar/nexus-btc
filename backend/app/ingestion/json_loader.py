"""Streaming JSON and NDJSON transaction loader."""

import json
from pathlib import Path
from typing import Generator, Any
from app.ingestion.normalizer import normalize_raw_record


class JsonLoader:
    """Robust JSON loader handling arrays of records or newline-delimited JSON."""

    @staticmethod
    def parse_content(
        content: str | bytes, source_file: str = "upload.json"
    ) -> Generator[tuple[dict[str, Any], list[str], str, int], None, None]:
        text = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else content
        text_stripped = text.strip()

        # Check if array
        if text_stripped.startswith("["):
            try:
                items = json.loads(text_stripped)
                for idx, item in enumerate(items, start=1):
                    if isinstance(item, dict):
                        canonical, flags, status = normalize_raw_record(item, source_file, idx)
                        yield canonical, flags, status, idx
                    else:
                        yield {"raw": item}, ["FLAG_INVALID_JSON_ELEMENT"], "INVALID", idx
                return
            except json.JSONDecodeError:
                pass  # Fallback to line by line

        # Try line by line (NDJSON)
        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                item = json.loads(line_str)
                if isinstance(item, dict):
                    canonical, flags, status = normalize_raw_record(item, source_file, idx)
                    yield canonical, flags, status, idx
                else:
                    yield {"raw": item}, ["FLAG_INVALID_JSON_ELEMENT"], "INVALID", idx
            except Exception as e:
                yield {"raw": line_str, "error": str(e)}, ["FLAG_JSON_PARSE_ERROR"], "INVALID", idx

    @classmethod
    def parse_file(
        cls, file_path: Path
    ) -> Generator[tuple[dict[str, Any], list[str], str, int], None, None]:
        with open(file_path, "rb") as f:
            content = f.read()
        yield from cls.parse_content(content, str(file_path))
