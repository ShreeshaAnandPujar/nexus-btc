"""Confidence Engine measuring evidence robustness independently from risk."""

class ConfidenceScoringEngine:
    """Computes a 0-100 confidence score based on telemetry completeness and mutual corroboration."""

    @staticmethod
    def compute_confidence(
        data_completeness_ratio: float,
        correlation_confidence: float,
        model_disagreement: float,
        has_motifs: bool,
        graph_degree: float,
    ) -> float:
        """
        Evaluate confidence score [0 - 100].
        Notice: High confidence can occur for a verified benign transaction,
        and low confidence can occur for a suspicious transaction with missing data.
        """
        # 1. Telemetry completeness [0 - 30 pts]
        c_data = data_completeness_ratio * 30.0

        # 2. Network correlation confidence [0 - 25 pts]
        c_corr = (correlation_confidence / 100.0) * 25.0

        # 3. Model agreement [0 - 25 pts]
        # Low disagreement -> high confidence
        disagreement_penalty = min(25.0, model_disagreement * 0.25)
        c_models = max(5.0, 25.0 - disagreement_penalty)

        # 4. Corroborating structural evidence [0 - 20 pts]
        c_evidence = 10.0 if has_motifs else 5.0
        if graph_degree >= 2:
            c_evidence += 10.0
        elif graph_degree >= 1:
            c_evidence += 5.0

        raw_conf = c_data + c_corr + c_models + c_evidence
        return round(max(10.0, min(100.0, raw_conf)), 2)
