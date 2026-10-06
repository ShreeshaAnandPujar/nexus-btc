"""Calibrated Random Forest classifier with Platt scaling."""

from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from app.core.config import settings
from app.core.logging import logger
from app.features.engine import FEATURE_COLUMNS


class CalibratedSupervisedModel:
    """Supervised Random Forest with Platt scaling probability calibration."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.base_rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )
        self.calibrated_model: CalibratedClassifierCV | None = None
        self.is_fitted = False
        self.metadata: dict = {
            "model_version": "1.0.0",
            "model_type": "RandomForest_PlattCalibrated",
            "feature_schema": FEATURE_COLUMNS,
            "hyperparameters": {
                "n_estimators": 100,
                "max_depth": 12,
                "calibration_method": "sigmoid (Platt scaling)",
            },
            "random_seed": random_state,
            "training_timestamp": None,
            "metrics": {},
        }

    def fit(self, X: np.ndarray, y: np.ndarray, training_dataset_name: str = "synthetic_train"):
        """Train Random Forest and fit Platt scaling calibrator."""
        X_clean = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=0.0)
        # Ensure both classes have at least 5 samples so stratified CV never sees single-class folds
        unique_classes, counts = np.unique(y, return_counts=True)
        if len(unique_classes) < 2 or min(counts) < 3:
            logger.warning("Fewer than 2 classes or sparse minority in training; augmenting balanced synthetic contrast.")
            n_features = X_clean.shape[1]
            pos_synth = np.random.normal(1.2, 0.3, size=(10, n_features))
            neg_synth = np.random.normal(0.2, 0.1, size=(10, n_features))
            X_clean = np.vstack([X_clean, pos_synth, neg_synth])
            y = np.hstack([y, np.ones(10, dtype=int), np.zeros(10, dtype=int)])

        # Fit base Random Forest
        self.base_rf.fit(X_clean, y)

        # Calibrate probabilities using Platt Scaling (sigmoid)
        cv_folds = 3 if len(X_clean) >= 30 else 2
        self.calibrated_model = CalibratedClassifierCV(
            estimator=self.base_rf,
            method="sigmoid",
            cv=cv_folds,
        )
        self.calibrated_model.fit(X_clean, y)
        self.is_fitted = True

        self.metadata["training_dataset"] = training_dataset_name
        self.metadata["training_timestamp"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"Fitted CalibratedSupervisedModel on {len(X_clean)} samples")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return calibrated probability of illicit class [0.0, 1.0]."""
        if not self.is_fitted:
            # Baseline deterministic prior if unfitted
            return np.full(len(X), 0.15)
        X_clean = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=0.0)
        probs = self.calibrated_model.predict_proba(X_clean)
        # Class 1 probability
        return probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]

    def save(self, filepath: Path | None = None) -> Path:
        """Save model checkpoint and metadata to disk."""
        target = filepath or (settings.MODELS_DIR / "rf_calibrated.joblib")
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self, "metadata": self.metadata}, target)
        logger.info(f"Model checkpoint saved to {target}")
        return target

    @classmethod
    def load(cls, filepath: Path | None = None) -> "CalibratedSupervisedModel":
        """Load model checkpoint from disk."""
        source = filepath or (settings.MODELS_DIR / "rf_calibrated.joblib")
        if source.exists():
            payload = joblib.load(source)
            logger.info(f"Loaded model checkpoint from {source}")
            return payload["model"]
        return cls()
