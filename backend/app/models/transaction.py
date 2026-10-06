"""SQLAlchemy models for canonical Bitcoin transactions."""

from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    Text,
    DateTime,
    Index,
)
from app.core.database import Base


class TransactionModel(Base):
    """Canonical transaction model in embedded SQLite."""

    __tablename__ = "transactions"

    record_id = Column(String(36), primary_key=True)
    source_file = Column(String(255), nullable=False)
    source_row = Column(Integer, nullable=False, default=1)
    ingestion_timestamp = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    validation_status = Column(String(32), nullable=False, default="VALID")
    data_quality_flags_json = Column(Text, nullable=False, default="[]")

    timestamp = Column(String(32), nullable=False, index=True)
    txid = Column(String(64), unique=True, nullable=False, index=True)

    # Network Telemetry
    src_ip = Column(String(45), nullable=True, index=True)
    dst_ip = Column(String(45), nullable=True)
    src_port = Column(Integer, nullable=True, default=8333)
    dst_port = Column(Integer, nullable=True, default=8333)
    country = Column(String(8), nullable=True, default="UNKNOWN")
    asn = Column(Integer, nullable=True, default=0)

    # UTXO Address Lists (stored as JSON arrays)
    input_addresses_json = Column(Text, nullable=False, default="[]")
    output_addresses_json = Column(Text, nullable=False, default="[]")
    input_amounts_json = Column(Text, nullable=False, default="[]")
    output_amounts_json = Column(Text, nullable=False, default="[]")

    # Aggregates
    input_amount = Column(Float, nullable=False, default=0.0)
    output_amount = Column(Float, nullable=False, default=0.0)
    fee = Column(Float, nullable=False, default=0.0)
    script_type = Column(String(32), nullable=True, default="UNKNOWN")

    # Forensic & Intelligence Annotations
    entity_id = Column(String(64), nullable=True, index=True)
    probable_cluster = Column(String(64), nullable=True)
    risk_score = Column(Float, nullable=False, default=0.0, index=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    alert_level = Column(String(16), nullable=False, default="NORMAL", index=True)
    detected_motifs_json = Column(Text, nullable=False, default="[]")

    # Helper properties for JSON columns
    @property
    def input_addresses(self) -> list[str]:
        return json.loads(self.input_addresses_json or "[]")

    @property
    def output_addresses(self) -> list[str]:
        return json.loads(self.output_addresses_json or "[]")

    @property
    def input_amounts(self) -> list[float]:
        return json.loads(self.input_amounts_json or "[]")

    @property
    def output_amounts(self) -> list[float]:
        return json.loads(self.output_amounts_json or "[]")

    @property
    def data_quality_flags(self) -> list[str]:
        return json.loads(self.data_quality_flags_json or "[]")

    @property
    def detected_motifs(self) -> list[str]:
        return json.loads(self.detected_motifs_json or "[]")


class GraphEdgeModel(Base):
    """Forensic graph edge cache for fast querying and Cytoscape serialization."""

    __tablename__ = "graph_edges"

    edge_id = Column(String(64), primary_key=True)
    txid = Column(String(64), nullable=False, index=True)
    source = Column(String(128), nullable=False, index=True)
    target = Column(String(128), nullable=False, index=True)
    relationship_type = Column(String(32), nullable=False, default="TRANSFERRED")
    amount = Column(Float, nullable=False, default=0.0)
    timestamp = Column(String(32), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    provenance = Column(String(32), nullable=False, default="OBSERVED")
