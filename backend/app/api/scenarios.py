"""Synthetic scenario generator endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.scenario import ScenarioGenerateRequest, ScenarioGenerateResponse, ScenarioInfo
from app.services.scenario_generator import ScenarioGenerator
from app.ingestion.engine import IngestionEngine
from app.services.pipeline import ForensicPipeline

router = APIRouter(prefix="/scenarios", tags=["Synthetic Scenario Studio"])


@router.get("/catalog", response_model=list[ScenarioInfo])
def get_scenario_catalog():
    """List all 12 supported synthetic forensic adversarial and benign scenarios."""
    return list(ScenarioGenerator.SCENARIO_CATALOG.values())


@router.post("/generate", response_model=ScenarioGenerateResponse)
def generate_scenario(
    req: ScenarioGenerateRequest,
    auto_ingest: bool = Query(True),
    db: Session = Depends(get_db),
):
    """
    Generate synthetic forensic scenario dataset with isolated ground truth.
    Optionally ingests and runs analysis automatically.
    """
    gen = ScenarioGenerator()
    resp, records = gen.generate(req)

    if auto_ingest:
        import json
        engine = IngestionEngine(db=db)
        engine.ingest_content(
            content=json.dumps(records),
            source_name=f"scenario_{req.scenario_type.lower()}_{req.seed}.json",
            format_hint="json",
        )
        pipeline = ForensicPipeline(db=db)
        pipeline.run_full_pipeline()

    return resp
