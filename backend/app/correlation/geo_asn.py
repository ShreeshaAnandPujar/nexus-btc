"""Offline GeoIP and ASN enrichment with graceful degradation."""

from pathlib import Path
from typing import Any
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger

try:
    import maxminddb
except ImportError:
    maxminddb = None


class GeoResult(BaseModel):
    available: bool = False
    country: str = "UNKNOWN"
    city: str | None = None
    asn: int = 0
    as_org: str | None = None
    status_message: str = "Geo enrichment unavailable"
    attribution: str = "MaxMind GeoLite2 / DB-IP (Local MMDB)"


class GeoEnricher:
    """Offline GeoIP lookup service supporting air-gapped MMDB files."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.GEOIP_DB_PATH
        self.reader = None
        self._init_reader()

    def _init_reader(self):
        if maxminddb is None:
            logger.info("maxminddb library not installed. Geo enrichment disabled.")
            return

        if self.db_path and self.db_path.exists() and self.db_path.is_file():
            try:
                self.reader = maxminddb.open_database(str(self.db_path))
                logger.info(f"Loaded local GeoIP database: {self.db_path}")
            except Exception as e:
                logger.warning(f"Failed opening GeoIP database at {self.db_path}: {e}")
                self.reader = None
        else:
            logger.info(f"GeoIP database not found at {self.db_path}. Running with graceful degradation.")

    def lookup(self, ip_str: str | None) -> GeoResult:
        """Lookup IP address; returns graceful fallback if unavailable."""
        if not ip_str or ip_str in ("0.0.0.0", "127.0.0.1", "UNKNOWN", ""):
            return GeoResult(available=False, status_message="Local/unspecified IP")

        if self.reader is None:
            return GeoResult(
                available=False,
                country="UNKNOWN",
                status_message="Geo enrichment unavailable (no local MMDB loaded)",
            )

        try:
            record: dict[str, Any] = self.reader.get(ip_str)
            if not record:
                return GeoResult(available=False, status_message="IP not found in local database")

            country = (
                record.get("country", {}).get("iso_code")
                or record.get("registered_country", {}).get("iso_code")
                or "UNKNOWN"
            )
            city = record.get("city", {}).get("names", {}).get("en")
            asn = record.get("autonomous_system_number", 0)
            as_org = record.get("autonomous_system_organization")

            return GeoResult(
                available=True,
                country=country.upper(),
                city=city,
                asn=asn,
                as_org=as_org,
                status_message="Enriched via local MMDB",
            )
        except Exception as e:
            return GeoResult(available=False, status_message=f"Lookup error: {e}")

    def close(self):
        if self.reader:
            try:
                self.reader.close()
            except Exception:
                pass
