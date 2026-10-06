"""Alert queue and forensic alert dossier endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import AlertModel
from app.models.transaction import TransactionModel
from app.schemas.alert import AlertQueueResponse, AlertSummary, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Forensic Alerts"])


@router.get("", response_model=AlertQueueResponse)
def get_alerts(
    severity: str | None = None,
    motif: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieve ranked alert queue prioritized by Risk and Confidence."""
    query = db.query(AlertModel)

    if severity:
        query = query.filter(AlertModel.severity == severity.upper())
    if motif:
        query = query.filter(AlertModel.primary_motif == motif.upper())

    total = query.count()
    critical_cnt = db.query(AlertModel).filter(AlertModel.severity == "CRITICAL").count()
    high_cnt = db.query(AlertModel).filter(AlertModel.severity == "HIGH").count()
    med_cnt = db.query(AlertModel).filter(AlertModel.severity == "MEDIUM").count()
    low_cnt = db.query(AlertModel).filter(AlertModel.severity == "LOW").count()

    # Prioritized sort: Risk descending, Confidence descending
    records = (
        query.order_by(AlertModel.risk_score.desc(), AlertModel.confidence_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    summaries = []
    for r in records:
        tx = db.query(TransactionModel).filter(TransactionModel.txid == r.txid).first()
        summaries.append(
            AlertSummary(
                alert_id=r.alert_id,
                txid=r.txid,
                entity_id=r.entity_id,
                risk_score=r.risk_score,
                confidence_score=r.confidence_score,
                severity=r.severity,
                primary_motif=r.primary_motif,
                created_at=r.created_at.isoformat(),
                status=r.status,
                amount_btc=tx.output_amount if tx else 0.0,
                country=tx.country if tx else "UNKNOWN",
            )
        )

    return AlertQueueResponse(
        total_alerts=total,
        critical_count=critical_cnt,
        high_count=high_cnt,
        medium_count=med_cnt,
        low_count=low_cnt,
        alerts=summaries,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    """Retrieve full forensic dossier for an alert, including evidence chain and explanations."""
    alert = db.query(AlertModel).filter(AlertModel.alert_id == alert_id).first()
    if not alert:
        # Check by TXID as fallback
        alert = db.query(AlertModel).filter(AlertModel.txid == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")

    return AlertResponse(
        alert_id=alert.alert_id,
        txid=alert.txid,
        entity_id=alert.entity_id,
        risk_score=alert.risk_score,
        confidence_score=alert.confidence_score,
        severity=alert.severity,
        primary_motif=alert.primary_motif,
        motifs=alert.motifs,
        created_at=alert.created_at.isoformat(),
        status=alert.status,
        explanation=alert.explanation,
        counterfactual=alert.counterfactual,
        evidence_chain=alert.evidence_chain,
        model_contributions=alert.model_contributions,
    )
