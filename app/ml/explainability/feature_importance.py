"""
Feature importance extraction for Software Reliability models.
"""

import numpy as np
from typing import Dict, Any, List, Optional

from app.ml.inference.model_loader import load_model
from app.ml.datasets.generate_dataset import FEATURE_COLUMNS


def get_feature_importance(model=None) -> Dict[str, Any]:
    """
    Extract feature importance from the trained model.

    Supports tree-based models (feature_importances_) and
    linear models (coef_).

    Returns:
        Dictionary with feature_importance dict and sorted ranking.
    """
    if model is None:
        model, _, _ = load_model()

    importance_dict = {}

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        for i, col in enumerate(FEATURE_COLUMNS):
            importance_dict[col] = round(float(importances[i]), 6)
    elif hasattr(model, "coef_"):
        coefs = np.abs(model.coef_[0]) if model.coef_.ndim > 1 else np.abs(model.coef_)
        for i, col in enumerate(FEATURE_COLUMNS):
            importance_dict[col] = round(float(coefs[i]), 6)
    else:
        # Fallback: equal importance
        for col in FEATURE_COLUMNS:
            importance_dict[col] = round(1.0 / len(FEATURE_COLUMNS), 6)

    # Sort by importance
    sorted_importance = sorted(
        importance_dict.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    return {
        "feature_importance": importance_dict,
        "ranking": [{"feature": f, "importance": v} for f, v in sorted_importance],
    }
