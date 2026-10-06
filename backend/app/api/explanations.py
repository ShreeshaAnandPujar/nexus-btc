"""Explainability and counterfactual analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import AlertModel
from app.schemas.explain import ExplanationResponse

router = APIRouter(prefix="/explanations", tags=["Explainability Studio"])


@router.get("/{alert_id}", response_model=ExplanationResponse)
def get_alert_explanation(alert_id: str, db: Session = Depends(get_db)):
    """Retrieve SHAP feature attributions, counterfactual deltas, and graph ablations for an alert."""
    alert = db.query(AlertModel).filter(AlertModel.alert_id == alert_id).first()
    if not alert:
        alert = db.query(AlertModel).filter(AlertModel.txid == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")

    expl_dict = alert.explanation
    if not expl_dict:
        raise HTTPException(status_code=404, detail="No explanation data available for this alert")

    return ExplanationResponse(**expl_dict)
