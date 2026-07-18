"""
Feature importance analysis for Software Reliability ML pipeline.

Provides model-agnostic permutation importance computation.
"""

import numpy as np
from sklearn.inspection import permutation_importance
from typing import Dict, Any, List


def compute_permutation_importance(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: List[str],
    n_repeats: int = 10,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Compute permutation-based feature importance.

    This is model-agnostic and works by shuffling each feature
    and measuring the drop in model performance.

    Returns:
        Dictionary with importance means, stds, and sorted ranking.
    """
    result = permutation_importance(
        model, X_test, y_test,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=-1,
    )

    importance_dict = {}
    for i, name in enumerate(feature_names):
        importance_dict[name] = {
            "mean": round(float(result.importances_mean[i]), 6),
            "std": round(float(result.importances_std[i]), 6),
        }

    ranking = sorted(
        importance_dict.items(),
        key=lambda x: x[1]["mean"],
        reverse=True,
    )

    return {
        "importance": importance_dict,
        "ranking": [{"feature": f, "mean": v["mean"], "std": v["std"]} for f, v in ranking],
    }
