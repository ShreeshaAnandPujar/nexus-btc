"""Ensemble Anomaly Detector combining independent ML models without hiding disagreement."""

import numpy as np
from app.models.transaction import TransactionModel
from app.anomaly.isolation_forest import IsolationForestDetector
from app.anomaly.supervised import CalibratedSupervisedModel
from app.anomaly.temporal_burst import TemporalBurstDetector
from app.core.logging import logger


class AnomalyEnsemble:
    """Ensemble of independent anomaly detectors preserving model disagreement."""

    def __init__(self):
        self.iforest = IsolationForestDetector()
        self.supervised_rf = CalibratedSupervisedModel.load()
        self.burst_detector = TemporalBurstDetector()

    def train_baseline(self, X: np.ndarray, y: np.ndarray | None = None):
        """Fit or warm-start ensemble models."""
        logger.info(f"Training AnomalyEnsemble baseline on {len(X)} samples...")
        self.iforest.fit(X)

        if y is not None:
            self.supervised_rf.fit(X, y)
            self.supervised_rf.save()
        elif not self.supervised_rf.is_fitted:
            # Pseudo-labels using Isolation Forest for initial warm-up
            if_scores = self.iforest.score_samples(X)
            pseudo_y = (if_scores >= 70.0).astype(int)
            self.supervised_rf.fit(X, pseudo_y, training_dataset_name="unsupervised_warmstart")
            self.supervised_rf.save()

    def infer(
        self, X: np.ndarray, transactions: list[TransactionModel]
    ) -> list[dict[str, float]]:
        """
        Run inference across all models.
        Returns array of model score dictionaries per sample.
        """
        if len(X) == 0:
            return []

        if not self.iforest.is_fitted:
            self.train_baseline(X)

        # 1. Isolation Forest scores [0 - 100]
        iforest_scores = self.iforest.score_samples(X)

        # 2. Supervised Calibrated RF probabilities [0.0 - 1.0] -> [0 - 100]
        rf_probs = self.supervised_rf.predict_proba(X)
        rf_scores = np.round(rf_probs * 100.0, 2)

        # 3. Temporal Burst scores [0 - 100]
        burst_map = self.burst_detector.detect_bursts(transactions)

        results = []
        for idx, tx in enumerate(transactions):
            if_s = float(iforest_scores[idx]) if idx < len(iforest_scores) else 0.0
            rf_s = float(rf_scores[idx]) if idx < len(rf_scores) else 0.0
            burst_s = float(burst_map.get(tx.txid, 0.0))

            # Measure model disagreement: absolute delta between supervised and unsupervised
            disagreement = round(abs(rf_s - if_s), 2)

            # Combined anomaly score
            combined = round((0.45 * rf_s) + (0.35 * if_s) + (0.20 * burst_s), 2)

            results.append({
                "iforest_score": if_s,
                "rf_calibrated_prob": round(float(rf_probs[idx]), 4) if idx < len(rf_probs) else 0.15,
                "rf_score": rf_s,
                "temporal_burst_score": burst_s,
                "model_disagreement": disagreement,
                "combined_anomaly_score": combined,
            })

        return results
