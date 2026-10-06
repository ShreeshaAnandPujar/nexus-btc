"""Canonical transaction schema and ingestion result models."""

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_TXID_HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
VALID_SCRIPT_TYPES = {"P2PK", "P2PKH", "P2SH", "P2WPKH", "P2TR", "UNKNOWN"}


class CanonicalTransaction(BaseModel):
    """Unified internal representation of one Bitcoin transaction record."""

    model_config = ConfigDict(strict=False, populate_by_name=True)

    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file: str = "direct_input"
    source_row: int = 1
    ingestion_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    validation_status: Literal["VALID", "WARNING", "REPAIRED", "INVALID"] = "VALID"
    data_quality_flags: list[str] = Field(default_factory=list)

    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    txid: str
    src_ip: str | None = "0.0.0.0"
    dst_ip: str | None = "0.0.0.0"
    src_port: int = 8333
    dst_port: int = 8333

    input_addresses: list[str] = Field(default_factory=list)
    output_addresses: list[str] = Field(default_factory=list)
    input_amounts: list[float] = Field(default_factory=list)
    output_amounts: list[float] = Field(default_factory=list)

    input_amount: float = 0.0
    output_amount: float = 0.0
    fee: float = 0.0
    script_type: str = "UNKNOWN"
    country: str = "UNKNOWN"
    asn: int = 0

    # Entity and ML annotations
    entity_id: str | None = None
    probable_cluster: str | None = None
    risk_score: float = 0.0
    confidence_score: float = 0.0
    alert_level: str = "NORMAL"
    detected_motifs: list[str] = Field(default_factory=list)

    @field_validator("txid")
    @classmethod
    def validate_txid(cls, v: str) -> str:
        v_clean = str(v).strip().lower()
        if not _TXID_HEX_RE.match(v_clean):
            # We don't crash, we note it in validation or repair
            if len(v_clean) == 64:
                return v_clean
            raise ValueError(f"Invalid txid length or characters: {v}")
        return v_clean

    @field_validator("script_type")
    @classmethod
    def validate_script_type(cls, v: str) -> str:
        v_upper = str(v).strip().upper()
        return v_upper if v_upper in VALID_SCRIPT_TYPES else "UNKNOWN"

    @model_validator(mode="after")
    def compute_aggregates(self) -> "CanonicalTransaction":
        # Calculate totals if not provided or 0
        if not self.input_amount and self.input_amounts:
            self.input_amount = round(sum(self.input_amounts), 8)
        if not self.output_amount and self.output_amounts:
            self.output_amount = round(sum(self.output_amounts), 8)
        if not self.fee and self.input_amount > self.output_amount:
            self.fee = round(self.input_amount - self.output_amount, 8)
        if self.fee < 0:
            self.fee = 0.0
        return self


class IngestResult(BaseModel):
    """Execution summary produced for every ingestion batch."""

    ingestion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file: str
    schema_version: str = "1.0.0"
    records_read: int = 0
    records_valid: int = 0
    records_invalid: int = 0
    duplicates: int = 0
    normalization_warnings: int = 0
    quarantined_path: str | None = None
    execution_time_seconds: float = 0.0
    status: str = "COMPLETED"
    message: str = "Ingestion completed successfully"
