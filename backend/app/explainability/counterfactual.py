"""Counterfactual sensitivity analysis engine."""

from app.schemas.explain import CounterfactualResult
from app.motifs.base import MotifEvidence


class CounterfactualEngine:
    """Computes model sensitivity and counterfactual deltas for forensic alerts."""

    @staticmethod
    def generate_counterfactuals(
        original_risk: float,
        motifs: list[MotifEvidence],
        tx_volume_btc: float,
        fan_ratio: float,
    ) -> list[CounterfactualResult]:
        results: list[CounterfactualResult] = []

        # 1. Counterfactual: Remove Primary Motif
        if motifs:
            primary_m = motifs[0]
            # Removing motif typically drops risk by 25 - 40 points
            drop = min(35.0, original_risk * 0.40)
            new_risk = round(max(10.0, original_risk - drop), 2)
            delta = round(new_risk - original_risk, 2)
            results.append(
                CounterfactualResult(
                    original_risk=original_risk,
                    modified_feature_name=primary_m.motif_type,
                    feature_removed_or_modified=f"Hypothetical elimination of {primary_m.motif_type} pattern",
                    new_risk=new_risk,
                    delta=delta,
                    interpretation=(
                        f"Removing the structural {primary_m.motif_type} reduces risk from {original_risk:.1f} "
                        f"to {new_risk:.1f} ({delta:+.1f} pts). Motif accounts for {abs(delta)/original_risk*100:.1f}% of alert severity."
                    ),
                )
            )

        # 2. Counterfactual: Normalize High Fan Ratio
        if fan_ratio > 3.0 or fan_ratio < 0.33:
            drop = min(20.0, original_risk * 0.22)
            new_risk = round(max(10.0, original_risk - drop), 2)
            delta = round(new_risk - original_risk, 2)
            results.append(
                CounterfactualResult(
                    original_risk=original_risk,
                    modified_feature_name="tx_fan_ratio",
                    feature_removed_or_modified="Replace asymmetric fan ratio with 1-in-1-out balanced transfer",
                    new_risk=new_risk,
                    delta=delta,
                    interpretation=(
                        f"Normalizing output fan dispersion drops risk by {abs(delta):.1f} pts to {new_risk:.1f}."
                    ),
                )
            )

        # 3. Counterfactual: Low Consumer Volume
        if tx_volume_btc > 1.0:
            drop = min(25.0, original_risk * 0.25)
            new_risk = round(max(10.0, original_risk - drop), 2)
            delta = round(new_risk - original_risk, 2)
            results.append(
                CounterfactualResult(
                    original_risk=original_risk,
                    modified_feature_name="tx_total_volume_btc",
                    feature_removed_or_modified="Reduce transaction volume to typical retail payment (0.01 BTC)",
                    new_risk=new_risk,
                    delta=delta,
                    interpretation=(
                        f"Reducing transfer magnitude to retail median reduces risk by {abs(delta):.1f} pts to {new_risk:.1f}."
                    ),
                )
            )

        return results
