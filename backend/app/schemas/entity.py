"""Schemas for inferred entity clusters."""

from pydantic import BaseModel, Field


class EntityResponse(BaseModel):
    entity_id: str
    cluster_type: str  # common_input, behavioral_cluster
    wallet_count: int
    member_wallets: list[str]
    cluster_confidence: float
    risk_score: float
    confidence_score: float
    total_volume_btc: float
    first_seen: str | None = None
    last_seen: str | None = None
    cluster_features: dict = Field(default_factory=dict)
    cluster_evidence: list[str] = Field(default_factory=list)
    recent_transactions: list[dict] = Field(default_factory=list)
    detected_motifs: list[str] = Field(default_factory=list)
    associated_ips: list[str] = Field(default_factory=list)


class EntitySummary(BaseModel):
    entity_id: str
    cluster_type: str
    wallet_count: int
    risk_score: float
    confidence_score: float
    total_volume_btc: float
