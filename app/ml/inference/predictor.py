"""
Predictor module for Software Reliability ML inference.

Loads the trained model and produces predictions from extracted feature vectors.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

from app.ml.inference.model_loader import load_model, is_model_available
from app.ml.inference.postprocessing import classify_risk_level, generate_recommendations
from app.ml.evaluation.metrics import compute_reliability_statistics
from app.ml.datasets.generate_dataset import FEATURE_COLUMNS


class ReliabilityPredictor:
    """
    Loads a trained model and produces reliability predictions for project metrics.
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata = {}
        self._loaded = False

    def load(self) -> None:
        """Load the trained model, scaler, and metadata from disk."""
        self.model, self.scaler, self.metadata = load_model()
        self._loaded = True

    def ensure_loaded(self) -> None:
        """Ensure the model is loaded before prediction."""
        if not self._loaded:
            self.load()

    @staticmethod
    def is_available() -> bool:
        """Check if a trained model exists on disk."""
        return is_model_available()

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict software reliability risk for a single set of extracted metrics.

        Args:
            features: Dictionary of extracted code metrics (from FeatureExtractor).

        Returns:
            Dictionary with:
                - predicted_label: 0 (no failure) or 1 (failure predicted)
                - failure_probability: float (0.0-1.0)
                - risk_level: 'Low', 'Medium', 'High', or 'Critical'
                - confidence_score: model confidence in prediction
                - reliability_stats: MTBF, failure intensity, R(t)
                - model_used: algorithm name
        """
        self.ensure_loaded()

        # Build DataFrame and apply derived features
        from app.ml.feature_engineering.build_features import build_derived_features
        df_single = pd.DataFrame([features])
        df_single = build_derived_features(df_single)

        target_cols = self.metadata.get("feature_columns", FEATURE_COLUMNS)
        feature_vector = []
        for col in target_cols:
            feature_vector.append(df_single[col].iloc[0] if col in df_single.columns else 0)

        X = np.array([feature_vector])

        # Scale if scaler is available
        if self.scaler is not None:
            X = self.scaler.transform(X)

        # Predict
        predicted_label = int(self.model.predict(X)[0])

        # Probability
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(X)[0]
            failure_probability = float(proba[1])
            confidence_score = float(max(proba))
        else:
            failure_probability = float(predicted_label)
            confidence_score = 1.0

        # Risk level
        risk_level = classify_risk_level(failure_probability)

        # Reliability statistics (MTBF, λ, R(t))
        reliability_stats = compute_reliability_statistics(failure_probability)

        return {
            "predicted_label": predicted_label,
            "failure_probability": round(failure_probability, 4),
            "risk_level": risk_level,
            "confidence_score": round(confidence_score, 4),
            "reliability_stats": reliability_stats,
            "model_used": self.metadata.get("algorithm", "unknown"),
        }


# Singleton instance
reliability_predictor = ReliabilityPredictor()
