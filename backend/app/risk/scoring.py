"""Calibrated Risk Engine incorporating independent forensic signals."""

from app.core.config import settings
from app.motifs.base import MotifEvidence


class RiskScoringEngine:
    """Computes a 0-100 risk score combining ML, motifs, network, and graph signals."""

    def __init__(
        self,
        w_anomaly: float | None = None,
        w_motif: float | None = None,
        w_network: float | None = None,
        w_graph: float | None = None,
    ):
        self.w_anomaly = w_anomaly if w_anomaly is not None else settings.WEIGHT_ANOMALY
        self.w_motif = w_motif if w_motif is not None else settings.WEIGHT_MOTIF
        self.w_network = w_network if w_network is not None else settings.WEIGHT_NETWORK
        self.w_graph = w_graph if w_graph is not None else settings.WEIGHT_GRAPH

        # Normalize weights so sum is 1.0
        tot = self.w_anomaly + self.w_motif + self.w_network + self.w_graph
        self.w_anomaly /= tot
        self.w_motif /= tot
        self.w_network /= tot
        self.w_graph /= tot

    def compute_risk(
        self,
        anomaly_score: float,
        motifs: list[MotifEvidence],
        network_score: float,
        graph_density: float,
        graph_degree: float,
    ) -> tuple[float, str, float]:
        """
        Calculate calibrated risk score.
        Returns: (risk_score [0-100], severity ['CRITICAL'|'HIGH'|'MEDIUM'|'LOW'], motif_contribution)
        """
        # Calculate motif score from detected evidence
        motif_score = 0.0
        if motifs:
            max_conf = max(m.confidence for m in motifs)
            # Motif severity weight
            type_weights = {
                "PEELING_CHAIN": 85.0,
                "MIXING_LIKE": 90.0,
                "RAPID_LAYERING": 85.0,
                "CIRCULAR_FLOW": 80.0,
                "DORMANT_ACTIVATION": 75.0,
                "RAPID_SPLIT": 75.0,
                "CONSOLIDATION": 65.0,
                "FAN_IN": 60.0,
                "FAN_OUT": 60.0,
            }
            base_m_scores = [type_weights.get(m.motif_type, 60.0) for m in motifs]
            motif_score = min(100.0, max(base_m_scores) * max_conf)

        # Graph structural risk
        graph_score = min(100.0, (graph_density * 50.0) + min(50.0, graph_degree * 2.0))

        # Fused risk score
        raw_risk = (
            (self.w_anomaly * anomaly_score)
            + (self.w_motif * motif_score)
            + (self.w_network * network_score)
            + (self.w_graph * graph_score)
        )
        risk_score = round(max(0.0, min(100.0, raw_risk)), 2)

        # Severity classification
        if risk_score >= 80.0:
            severity = "CRITICAL"
        elif risk_score >= 65.0:
            severity = "HIGH"
        elif risk_score >= 40.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return risk_score, severity, round(motif_score, 2)
