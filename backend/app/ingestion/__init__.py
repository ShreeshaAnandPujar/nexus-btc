"""Ingestion package for NEXUS-BTC."""

from app.ingestion.engine import IngestionEngine
from app.ingestion.detector import detect_format
from app.ingestion.csv_loader import CsvLoader
from app.ingestion.json_loader import JsonLoader
from app.ingestion.xml_loader import XmlLoader
from app.ingestion.normalizer import normalize_raw_record
from app.ingestion.quarantine import QuarantineManager

__all__ = [
    "IngestionEngine",
    "detect_format",
    "CsvLoader",
    "JsonLoader",
    "XmlLoader",
    "normalize_raw_record",
    "QuarantineManager",
]
