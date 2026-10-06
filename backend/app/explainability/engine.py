"""Unified Explainability and Counterfactual Engine."""

import numpy as np
from app.models.transaction import TransactionModel
from app.motifs.base import MotifEvidence
from app.schemas.explain import ExplanationResponse
from app.explainability.shap_explainer import ShapExplainer
from app.explainability.counterfactual import CounterfactualEngine
from app.explainability.graph_ablation import GraphAblationEngine


class ExplainabilityEngine:
    """Provides transparent multimodal explanations (SHAP + Counterfactuals + Graph Ablation)."""

    def __init__(self, tree_estimator=None):
        self.shap_explainer = ShapExplainer(tree_estimator)
        self.counterfactual_engine = CounterfactualEngine()
        self.ablation_engine = GraphAblationEngine()

    def explain(
        self,
        alert_id: str,
        tx: TransactionModel,
        feature_vec: np.ndarray,
        risk_score: float,
        motifs: list[MotifEvidence],
        model_scores: dict[str, float] | None = None,
        graph_degree: float = 2.0,
    ) -> ExplanationResponse:
        base_expected = 18.5  # Typical baseline benign prior

        # 1. SHAP / Deterministic Feature Attributions
        attributions = self.shap_explainer.explain_sample(
            feature_vec, base_value=base_expected, final_risk=risk_score
        )

        # 2. Counterfactual sensitivity deltas
        fan_ratio = len(tx.output_addresses) / (len(tx.input_addresses) + 1e-8)
        counterfactuals = self.counterfactual_engine.generate_counterfactuals(
            original_risk=risk_score,
            motifs=motifs,
            tx_volume_btc=tx.output_amount,
            fan_ratio=fan_ratio,
        )

        # 3. Graph topological ablations
        ablations = self.ablation_engine.ablate_structures(
            original_risk=risk_score,
            motifs=motifs,
            graph_degree=graph_degree,
        )

        # Model contributions
        mod_contribs = model_scores or {
            "random_forest": round(risk_score * 0.45, 1),
            "isolation_forest": round(risk_score * 0.35, 1),
            "temporal_burst": round(risk_score * 0.20, 1),
        }

        # Human-readable summary
        top_feat = attributions[0].display_name if attributions else "behavioral volume"
        motif_summary = f"driven by {motifs[0].motif_type}" if motifs else "driven by statistical anomaly"
        summary = (
            f"Alert priority {risk_score:.1f}/100 is predominantly {motif_summary}, with "
            f"'{top_feat}' showing greatest positive attribution."
        )

        return ExplanationResponse(
            alert_id=alert_id,
            txid=tx.txid,
            base_expected_value=base_expected,
            final_risk_score=risk_score,
            top_feature_attributions=attributions[:8],
            model_contributions=mod_contribs,
            counterfactuals=counterfactuals,
            graph_ablations=ablations,
            forensic_summary=summary,
        )
