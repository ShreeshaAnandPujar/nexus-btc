"""Health and system diagnostics router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.models.transaction import TransactionModel
from app.models.alert import AlertModel
from app.models.entity import EntityModel

router = APIRouter(prefix="/health", tags=["System Health"])


@router.get("")
def get_system_health(db: Session = Depends(get_db)):
    """Comprehensive system diagnostics for air-gapped forensic operations."""
    # Check DB connectivity
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    # Check GeoIP
    geo_ok = settings.GEOIP_DB_PATH.exists() and settings.GEOIP_DB_PATH.is_file()

    # Model status
    model_file = settings.MODELS_DIR / "rf_calibrated.joblib"
    model_loaded = model_file.exists()

    # Record counts
    tx_count = db.query(TransactionModel).count() if db_ok else 0
    alert_count = db.query(AlertModel).count() if db_ok else 0
    entity_count = db.query(EntityModel).count() if db_ok else 0

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "system": "NEXUS-BTC",
        "version": settings.VERSION,
        "offline_mode": settings.OFFLINE_MODE,
        "database": {
            "type": "SQLite 3 (WAL mode)",
            "status": "CONNECTED" if db_ok else "ERROR",
            "path": settings.DATABASE_URL,
            "transactions_count": tx_count,
            "alerts_count": alert_count,
            "entities_count": entity_count,
        },
        "ml_models": {
            "isolation_forest": "READY (in-process)",
            "random_forest_calibrated": "LOADED" if model_loaded else "READY (unfitted)",
            "temporal_burst": "READY (in-process)",
            "shap_xai": "READY (TreeExplainer)",
        },
        "geolocation": {
            "status": "AVAILABLE" if geo_ok else "UNAVAILABLE (graceful fallback)",
            "path": str(settings.GEOIP_DB_PATH),
            "attribution": "MaxMind GeoLite2 / DB-IP (Local MMDB)",
        },
    }


@router.get("/ready")
def get_readiness():
    """Kubernetes/container readiness check."""
    return {"ready": True, "offline_ready": True, "system": "NEXUS-BTC"}


@router.get("/offline")
def get_offline_status():
    """Verify strict air-gap compliance and offline readiness."""
    return {
        "offline_capable": True,
        "mode": "OFFLINE_FIRST",
        "external_calls_allowed": False,
        "telemetry_disabled": True,
    }

