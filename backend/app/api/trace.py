"""Value-aware fund tracing endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.trace import TraceRequest, TraceResponse
from app.tracing.best_first_tracer import BestFirstFundTracer

router = APIRouter(prefix="/trace", tags=["Fund Tracing"])


@router.post("", response_model=TraceResponse)
def trace_funds(req: TraceRequest, db: Session = Depends(get_db)):
    """
    Execute Value-Aware Best-First search forward or backward along UTXO paths.
    Avoids exponential graph explosion and identifies forensic terminal endpoints.
    """
    tracer = BestFirstFundTracer(db=db)
    return tracer.trace(req)
