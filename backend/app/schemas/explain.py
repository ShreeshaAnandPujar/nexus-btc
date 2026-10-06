"""Schemas for Explainability (SHAP, Counterfactual, Graph Ablation)."""

from pydantic import BaseModel, Field


class FeatureAttribution(BaseModel):
    feature_name: str
    feature_value: float
    contribution: float  # SHAP value
    display_name: str
    category: str  # transaction, graph, network
    interpretation: str


class CounterfactualResult(BaseModel):
    original_risk: float
    modified_feature_name: str
    feature_removed_or_modified: str
    new_risk: float
    delta: float  # new_risk - original_risk
    interpretation: str


class GraphAblationResult(BaseModel):
    original_risk: float
    ablated_motif_or_subgraph: str
    risk_after_ablation: float
    delta: float
    structural_influence_pct: float


class ExplanationResponse(BaseModel):
    alert_id: str
    txid: str
    base_expected_value: float
    final_risk_score: float
    top_feature_attributions: list[FeatureAttribution]
    model_contributions: dict[str, float]
    counterfactuals: list[CounterfactualResult]
    graph_ablations: list[GraphAblationResult]
    forensic_summary: str
