"""
SHAP Explainability module for Software Reliability predictions.

Generates SHAP feature attribution values to explain why a model
made a particular reliability prediction.
"""

import numpy as np
import shap
from typing import Dict, Any, List, Optional

from app.ml.inference.model_loader import load_model
from app.ml.datasets.generate_dataset import FEATURE_COLUMNS


class ShapExplainer:
    """
    Wraps SHAP TreeExplainer or KernelExplainer to produce
    feature contribution values for individual predictions.
    """

    def __init__(self):
        self.explainer = None
        self.model = None
        self.scaler = None
        self.metadata = {}
        self._initialized = False

    def initialize(self) -> None:
        """Load model and create SHAP explainer."""
        self.model, self.scaler, self.metadata = load_model()

        # Use TreeExplainer for tree-based models, KernelExplainer for others
        algorithm = self.metadata.get("algorithm", "")
        tree_algorithms = ["random_forest", "xgboost", "lightgbm", "catboost", "decision_tree"]

        target_cols = self.metadata.get("feature_columns", FEATURE_COLUMNS)
        if algorithm in tree_algorithms:
            self.explainer = shap.TreeExplainer(self.model)
        else:
            # KernelExplainer needs a background dataset; use a small dummy sample
            background = np.zeros((10, len(target_cols)))
            self.explainer = shap.KernelExplainer(self.model.predict_proba, background)

        self._initialized = True

    def ensure_initialized(self) -> None:
        """Ensure the explainer is initialized."""
        if not self._initialized:
            self.initialize()

    def explain(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SHAP explanation for a single prediction.

        Args:
            features: Dictionary of extracted code metrics.

        Returns:
            Dictionary with:
                - shap_values: dict of feature_name → SHAP value
                - feature_contributions: sorted list of (feature, value) tuples
                - top_risk_factors: top 5 features contributing to failure risk
                - base_value: model's base prediction value
        """
        self.ensure_initialized()

        # Build DataFrame and apply derived features
        import pandas as pd
        from app.ml.feature_engineering.build_features import build_derived_features

        target_cols = self.metadata.get("feature_columns", FEATURE_COLUMNS)
        df_single = pd.DataFrame([features])
        df_single = build_derived_features(df_single)

        feature_vector = []
        for col in target_cols:
            feature_vector.append(df_single[col].iloc[0] if col in df_single.columns else 0)

        X = np.array([feature_vector])

        # Scale
        if self.scaler is not None:
            X = self.scaler.transform(X)

        # Compute SHAP values
        shap_values = self.explainer.shap_values(X)

        # Handle multi-output (binary classification returns list of 2 arrays, or a 3D array)
        if isinstance(shap_values, list):
            # Use class 1 (failure) SHAP values
            sv = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif isinstance(shap_values, np.ndarray):
            if shap_values.ndim == 3:
                # Shape (N, M, C), select first sample, class 1
                sv = shap_values[0, :, 1] if shap_values.shape[2] > 1 else shap_values[0, :, 0]
            elif shap_values.ndim == 2:
                # Shape (N, M)
                sv = shap_values[0]
            else:
                sv = shap_values.flatten()
        else:
            sv = np.asarray(shap_values).flatten()

        # Map to feature names
        shap_dict = {}
        for i, col in enumerate(target_cols):
            shap_dict[col] = round(float(sv[i]), 6)

        # Sort by absolute contribution
        sorted_contributions = sorted(
            shap_dict.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        # Top risk factors (positive SHAP = increases failure risk)
        top_risk_factors = [
            {"feature": feat, "shap_value": val, "direction": "increases risk" if val > 0 else "decreases risk"}
            for feat, val in sorted_contributions[:5]
        ]

        # Base value
        base_value = None
        if hasattr(self.explainer, "expected_value"):
            ev = self.explainer.expected_value
            if isinstance(ev, (list, np.ndarray)):
                base_value = float(ev[1]) if len(ev) > 1 else float(ev[0])
            else:
                base_value = float(ev)

        return {
            "shap_values": shap_dict,
            "feature_contributions": sorted_contributions,
            "top_risk_factors": top_risk_factors,
            "base_value": base_value,
        }


# Singleton instance
shap_explainer = ShapExplainer()
