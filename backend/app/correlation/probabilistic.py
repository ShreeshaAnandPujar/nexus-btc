"""Probabilistic Network-to-Blockchain Correlation Engine."""

from datetime import datetime
from pydantic import BaseModel, Field


class CorrelationEvidence(BaseModel):
    association_score: float  # 0 to 100
    association_confidence: float  # 0 to 100
    association_reasons: list[str] = Field(default_factory=list)
    relationship_type: str = "PROBABILISTIC"  # DIRECT, INFERRED, PROBABILISTIC
    disclaimer: str = (
        "Forensic Attribution Notice: Network relay observations represent packet propagation "
        "and do not constitute proof of human identity or legal wallet ownership."
    )


class ProbabilisticCorrelator:
    """Evaluates multi-factor correlation between network observations and on-chain events."""

    @staticmethod
    def correlate(
        tx_timestamp: str,
        net_timestamp: str | None = None,
        ip_observation_count: int = 1,
        cluster_observed_ips: list[str] | None = None,
        target_ip: str = "0.0.0.0",
        asn: int = 0,
        country: str = "UNKNOWN",
    ) -> CorrelationEvidence:
        reasons: list[str] = []
        score_components: list[float] = []
        confidence_components: list[float] = []

        # 1. Direct or temporal closeness
        if net_timestamp:
            try:
                t_tx = datetime.fromisoformat(tx_timestamp.replace("Z", "+00:00"))
                t_net = datetime.fromisoformat(net_timestamp.replace("Z", "+00:00"))
                delta_sec = abs((t_tx - t_net).total_seconds())

                if delta_sec <= 2.0:
                    score_components.append(95.0)
                    confidence_components.append(90.0)
                    reasons.append(f"Sub-second broadcast alignment (delta={delta_sec:.2f}s)")
                elif delta_sec <= 30.0:
                    score_components.append(80.0)
                    confidence_components.append(75.0)
                    reasons.append(f"Near-synchronous propagation (delta={delta_sec:.1f}s)")
                elif delta_sec <= 300.0:
                    score_components.append(50.0)
                    confidence_components.append(60.0)
                    reasons.append(f"P2P relay window match (delta={delta_sec:.0f}s)")
                else:
                    score_components.append(20.0)
                    confidence_components.append(40.0)
                    reasons.append(f"Extended temporal gap (delta={delta_sec:.0f}s)")
            except Exception:
                pass

        # 2. Repeated network observations
        if ip_observation_count > 10:
            score_components.append(85.0)
            confidence_components.append(85.0)
            reasons.append(f"High-frequency relay node ({ip_observation_count} observations)")
        elif ip_observation_count > 2:
            score_components.append(65.0)
            confidence_components.append(70.0)
            reasons.append(f"Repeated emission point ({ip_observation_count} observations)")
        else:
            score_components.append(40.0)
            confidence_components.append(50.0)
            reasons.append("Isolated network observation")

        # 3. Cluster IP consistency
        if cluster_observed_ips and target_ip in cluster_observed_ips:
            score_components.append(80.0)
            confidence_components.append(75.0)
            reasons.append(f"IP previously associated with entity cluster")

        # 4. Routing / ASN consistency
        if asn > 0:
            confidence_components.append(70.0)
            reasons.append(f"BGP Autonomous System ASN-{asn} confirmed")

        if country != "UNKNOWN":
            confidence_components.append(65.0)
            reasons.append(f"Geographic routing point: {country}")

        # Compute composite scores
        assoc_score = (
            round(sum(score_components) / len(score_components), 2)
            if score_components
            else 50.0
        )
        assoc_conf = (
            round(sum(confidence_components) / len(confidence_components), 2)
            if confidence_components
            else 50.0
        )

        rel_type = "DIRECT" if (net_timestamp and assoc_score >= 90.0) else (
            "INFERRED" if (ip_observation_count > 3) else "PROBABILISTIC"
        )

        return CorrelationEvidence(
            association_score=assoc_score,
            association_confidence=assoc_conf,
            association_reasons=reasons,
            relationship_type=rel_type,
        )
