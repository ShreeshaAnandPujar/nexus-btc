"""Schemas for alerts, queue, and forensic evidence chain."""

from pydantic import BaseModel, Field
from datetime import datetime


class EvidenceChainStep(BaseModel):
    step_number: int
    step_type: str  # NETWORK_OBSERVATION, TRANSACTION, INPUT_WALLET, OUTPUT_WALLET, ENTITY, NEXT_TRANSACTION, MOTIF
    identifier: str
    description: str
    relationship: str  # observed, inferred, probabilistic
    confidence: float
    metadata: dict = Field(default_factory=dict)


class AlertResponse(BaseModel):
    alert_id: str
    txid: str
    entity_id: str | None = None
    risk_score: float
    confidence_score: float
    severity: str
    primary_motif: str | None = None
    motifs: list[str] = Field(default_factory=list)
    created_at: str
    status: str
    explanation: dict = Field(default_factory=dict)
    counterfactual: list[dict] = Field(default_factory=list)
    evidence_chain: list[EvidenceChainStep] = Field(default_factory=list)
    model_contributions: dict = Field(default_factory=dict)


class AlertSummary(BaseModel):
    alert_id: str
    txid: str
    entity_id: str | None = None
    risk_score: float
    confidence_score: float
    severity: str
    primary_motif: str | None = None
    created_at: str
    status: str
    amount_btc: float = 0.0
    country: str = "UNKNOWN"


class AlertQueueResponse(BaseModel):
    total_alerts: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    alerts: list[AlertSummary]
