"""Isolation Forest baseline unsupervised anomaly detector."""

import numpy as np
from sklearn.ensemble import IsolationForest
from app.core.logging import logger


class IsolationForestDetector:
    """Unsupervised tree isolation detector for multivariate transaction outliers."""

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """Fit Isolation Forest on feature matrix."""
        X_clean = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=0.0)
        if len(X_clean) < 10:
            logger.info("Insufficient samples (<10) to train Isolation Forest; using default fit.")
            # Synthesize standard distribution if initial dataset is small
            X_init = np.vstack([X_clean, np.random.normal(0.5, 0.2, (20, X_clean.shape[1]))]) if len(X_clean) > 0 else np.random.normal(0, 1, (20, 14))
            self.model.fit(X_init)
        else:
            self.model.fit(X_clean)
        self.is_fitted = True

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly score normalized to [0, 100].
        Lower score_samples in sklearn means more anomalous, so we invert.
        """
        if not self.is_fitted:
            self.fit(X)

        X_clean = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=0.0)
        raw_scores = self.model.score_samples(X_clean)
        # raw_scores typically range from -0.8 to -0.2
        # Normalize into 0-100 where 100 is highly anomalous
        normalized = np.clip((-raw_scores - 0.3) / 0.5 * 100.0, 0.0, 100.0)
        return np.round(normalized, 2)
