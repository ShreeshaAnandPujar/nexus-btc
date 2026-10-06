"""SQLAlchemy model for clustered entities."""

from datetime import datetime, timezone
import json
from sqlalchemy import Column, String, Float, Integer, Text, DateTime
from app.core.database import Base


class EntityModel(Base):
    """Forensic inferred entity cluster record."""

    __tablename__ = "entities"

    entity_id = Column(String(64), primary_key=True)
    cluster_type = Column(String(32), nullable=False, default="common_input")  # common_input, behavioral_hdbscan
    wallet_count = Column(Integer, nullable=False, default=1)
    member_wallets_json = Column(Text, nullable=False, default="[]")
    
    cluster_confidence = Column(Float, nullable=False, default=0.85)
    risk_score = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=0.0)
    
    cluster_features_json = Column(Text, nullable=False, default="{}")
    cluster_evidence_json = Column(Text, nullable=False, default="[]")
    
    first_seen = Column(String(32), nullable=True)
    last_seen = Column(String(32), nullable=True)
    total_volume_btc = Column(Float, nullable=False, default=0.0)
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def member_wallets(self) -> list[str]:
        return json.loads(self.member_wallets_json or "[]")

    @property
    def cluster_features(self) -> dict:
        return json.loads(self.cluster_features_json or "{}")

    @property
    def cluster_evidence(self) -> list[str]:
        return json.loads(self.cluster_evidence_json or "[]")
