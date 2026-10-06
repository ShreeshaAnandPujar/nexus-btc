"""Configuration management for NEXUS-BTC.
Offline-first, zero cloud dependencies.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root determination
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """System settings with secure, air-gapped offline defaults."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "NEXUS-BTC"
    VERSION: str = "1.0.0"
    OFFLINE_MODE: bool = True
    DEBUG: bool = False

    # Storage paths
    PROJECT_ROOT_PATH: Path = PROJECT_ROOT
    DATA_DIR: Path = PROJECT_ROOT / "data"
    QUARANTINE_DIR: Path = PROJECT_ROOT / "data" / "normalized" / "quarantine"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    GEO_DIR: Path = PROJECT_ROOT / "geo"
    REPORTS_DIR: Path = PROJECT_ROOT / "reports"

    # SQLite database URL (WAL mode)
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'nexus_forensics.db'}"

    # Offline GeoIP database (optional local MMDB)
    GEOIP_DB_PATH: Path = PROJECT_ROOT / "geo" / "GeoLite2-City.mmdb"

    # Ingestion constraints
    MAX_UPLOAD_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB limit
    BATCH_SIZE: int = 500

    # Risk weights
    WEIGHT_ANOMALY: float = 0.30
    WEIGHT_MOTIF: float = 0.35
    WEIGHT_NETWORK: float = 0.20
    WEIGHT_GRAPH: float = 0.15

    # Thresholds
    ALERT_THRESHOLD_HIGH: float = 75.0
    ALERT_THRESHOLD_MEDIUM: float = 50.0

    # Fund tracing parameters
    DEFAULT_MAX_HOPS: int = 10
    DEFAULT_MAX_NODES: int = 100
    DEFAULT_MIN_VALUE_RATIO: float = 0.01  # 1%


settings = Settings()

# Ensure standard directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.GEO_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
