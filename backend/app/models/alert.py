"""SQLAlchemy model for prioritized forensic alerts."""

from datetime import datetime, timezone
import json
from sqlalchemy import Column, String, Float, Text, DateTime, Index
from app.core.database import Base


class AlertModel(Base):
    """Forensic alert record with explainability and evidence chain."""

    __tablename__ = "alerts"

    alert_id = Column(String(64), primary_key=True)
    txid = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(64), nullable=True, index=True)
    
    risk_score = Column(Float, nullable=False, default=0.0, index=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    severity = Column(String(16), nullable=False, default="LOW", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    
    primary_motif = Column(String(64), nullable=True, index=True)
    motifs_json = Column(Text, nullable=False, default="[]")
    
    explanation_json = Column(Text, nullable=False, default="{}")
    counterfactual_json = Column(Text, nullable=False, default="[]")
    evidence_chain_json = Column(Text, nullable=False, default="[]")
    model_contributions_json = Column(Text, nullable=False, default="{}")
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    status = Column(String(16), nullable=False, default="OPEN")  # OPEN, INVESTIGATING, CLOSED

    @property
    def motifs(self) -> list[str]:
        return json.loads(self.motifs_json or "[]")

    @property
    def explanation(self) -> dict:
        return json.loads(self.explanation_json or "{}")

    @property
    def counterfactual(self) -> list[dict]:
        val = json.loads(self.counterfactual_json or "[]")
        if isinstance(val, dict):
            return [val] if val else []
        return val

    @property
    def evidence_chain(self) -> list[dict]:
        return json.loads(self.evidence_chain_json or "[]")

    @property
    def model_contributions(self) -> dict:
        return json.loads(self.model_contributions_json or "{}")
