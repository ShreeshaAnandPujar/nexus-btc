"""Data ingestion and pipeline orchestration endpoints."""

from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.canonical import IngestResult
from app.ingestion.engine import IngestionEngine
from app.services.pipeline import ForensicPipeline

router = APIRouter(prefix="", tags=["Ingestion & Pipeline"])


@router.post("/ingest", response_model=IngestResult)
async def ingest_file(
    file: UploadFile = File(...),
    run_pipeline: bool = Form(True),
    db: Session = Depends(get_db),
):
    """
    Ingest multi-format transaction batches (CSV, JSON, XML).
    Defensively sanitizes input, quarantines invalid rows, and avoids crashing.
    """
    contents = await file.read()
    from pathlib import Path
    from app.security.validator import validate_file_upload, SecurityError
    
    raw_filename = file.filename or "upload.csv"
    safe_name = Path(raw_filename).name
    try:
        validate_file_upload(safe_name, len(contents))
    except SecurityError as se:
        raise HTTPException(status_code=400, detail=str(se))

    engine = IngestionEngine(db=db)

    try:
        result = engine.ingest_content(
            content=contents,
            source_name=safe_name,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {e}")

    # Optionally trigger forensic pipeline immediately
    if run_pipeline and result.records_valid > 0:
        pipeline = ForensicPipeline(db=db)
        pipeline.run_full_pipeline()

    return result


@router.post("/ingest/sample", response_model=IngestResult)
def ingest_sample(
    file_type: str = "csv",
    run_pipeline: bool = True,
    db: Session = Depends(get_db),
):
    """
    Ingest pre-packaged forensic sample dataset (CSV, JSON, XML) without file upload.
    """
    from pathlib import Path
    from app.core.config import settings

    filename = f"transactions_sample.{file_type.lower()}"
    sample_path = settings.PROJECT_ROOT_PATH / "data" / "sample" / filename
    if not sample_path.exists():
        # Fallback to csv
        sample_path = settings.PROJECT_ROOT_PATH / "data" / "sample" / "transactions_sample.csv"

    with open(sample_path, "rb") as f:
        content = f.read()

    engine = IngestionEngine(db=db)
    result = engine.ingest_content(
        content=content,
        source_name=sample_path.name,
    )

    if run_pipeline and result.records_valid > 0:
        pipeline = ForensicPipeline(db=db)
        pipeline.run_full_pipeline()

    return result


@router.post("/pipeline/run")
def trigger_pipeline(db: Session = Depends(get_db)):
    """Trigger full 14-stage forensic analysis across all ingested transactions."""
    pipeline = ForensicPipeline(db=db)
    summary = pipeline.run_full_pipeline()
    return summary

