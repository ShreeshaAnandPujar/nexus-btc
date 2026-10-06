"""Master API Router uniting all NEXUS-BTC forensic endpoints."""

from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api.alerts import router as alerts_router
from app.api.entities import router as entities_router
from app.api.transactions import router as transactions_router
from app.api.graph import router as graph_router
from app.api.trace import router as trace_router
from app.api.scenarios import router as scenarios_router
from app.api.models import router as models_router
from app.api.explanations import router as explanations_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(ingest_router)
api_router.include_router(alerts_router)
api_router.include_router(entities_router)
api_router.include_router(transactions_router)
api_router.include_router(graph_router)
api_router.include_router(trace_router)
api_router.include_router(scenarios_router)
api_router.include_router(models_router)
api_router.include_router(explanations_router)
