"""Base schema and interface for laundering motif detectors."""

import uuid
from typing import Any
from pydantic import BaseModel, Field


class MotifEvidence(BaseModel):
    """Structured evidence returned by a laundering pattern detector."""

    motif_id: str = Field(default_factory=lambda: f"MOTIF-{uuid.uuid4().hex[:8].upper()}")
    motif_type: str
    transactions: list[str] = Field(default_factory=list)
    wallets: list[str] = Field(default_factory=list)
    hops: int = 1
    duration_seconds: float = 0.0
    value_preservation: float = 1.0
    confidence: float = 0.80
    details: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""


class BaseMotifDetector:
    """Base class for motif detectors."""

    motif_type: str = "UNKNOWN"

    def detect(self, *args, **kwargs) -> list[MotifEvidence]:
        raise NotImplementedError
