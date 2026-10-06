"""Schemas for Synthetic Adversarial Scenario Generator."""

from pydantic import BaseModel, Field
from typing import Literal

ScenarioType = Literal[
    "NORMAL_TRANSACTION",
    "LEGITIMATE_EXCHANGE",
    "PEELING_CHAIN",
    "FAN_IN",
    "FAN_OUT",
    "RAPID_LAYERING",
    "MIXING_LIKE",
    "CIRCULAR_FLOW",
    "DORMANT_ACTIVATION",
    "SUSPICIOUS_CONSOLIDATION",
    "BENIGN_FALSE_POSITIVE",
    "ADVERSARIAL_TIMING_VARIATION",
]


class ScenarioGenerateRequest(BaseModel):
    scenario_type: ScenarioType
    seed: int = 42
    transaction_count: int = 25
    base_volume_btc: float = 10.0
    inject_noise: bool = True


class ScenarioInfo(BaseModel):
    scenario_id: str
    scenario_type: str
    title: str
    description: str
    expected_pattern: str
    ground_truth_illicit: bool
    expected_motifs: list[str]


class ScenarioGenerateResponse(BaseModel):
    scenario_id: str
    scenario_type: str
    record_count: int
    ground_truth_label: str  # ILLICIT or BENIGN
    expected_motifs: list[str]
    parameters: dict
    output_filepath: str
    message: str
