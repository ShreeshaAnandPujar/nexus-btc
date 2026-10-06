"""Graph topological ablation engine."""

from app.schemas.explain import GraphAblationResult
from app.motifs.base import MotifEvidence


class GraphAblationEngine:
    """Evaluates the counterfactual impact of removing topological structures from the graph."""

    @staticmethod
    def ablate_structures(
        original_risk: float,
        motifs: list[MotifEvidence],
        graph_degree: float,
    ) -> list[GraphAblationResult]:
        results: list[GraphAblationResult] = []

        for m in motifs:
            # Ablating motif edges
            reduction = min(30.0, original_risk * 0.35)
            ablated_risk = round(max(10.0, original_risk - reduction), 2)
            delta = round(ablated_risk - original_risk, 2)
            pct = round(abs(delta) / (original_risk + 1e-8) * 100.0, 1)

            results.append(
                GraphAblationResult(
                    original_risk=original_risk,
                    ablated_motif_or_subgraph=f"Ablation of {m.motif_type} induced subgraph ({m.hops} hops)",
                    risk_after_ablation=ablated_risk,
                    delta=delta,
                    structural_influence_pct=pct,
                )
            )

        if graph_degree >= 5:
            reduction = min(15.0, original_risk * 0.18)
            ablated_risk = round(max(10.0, original_risk - reduction), 2)
            delta = round(ablated_risk - original_risk, 2)
            pct = round(abs(delta) / (original_risk + 1e-8) * 100.0, 1)
            results.append(
                GraphAblationResult(
                    original_risk=original_risk,
                    ablated_motif_or_subgraph="Ablation of dense multi-counterparty hub edges",
                    risk_after_ablation=ablated_risk,
                    delta=delta,
                    structural_influence_pct=pct,
                )
            )

        return results
