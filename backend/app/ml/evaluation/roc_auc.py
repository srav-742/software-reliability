"""
ROC-AUC curve data generation for Software Reliability evaluation.
"""

import numpy as np
from sklearn.metrics import roc_curve, auc
from typing import Dict, Any


def compute_roc_curve(
    y_true: np.ndarray,
    y_proba: np.ndarray,
) -> Dict[str, Any]:
    """
    Compute ROC curve data points and AUC score.

    Returns:
        Dictionary with fpr, tpr arrays (as lists), thresholds, and auc_score.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)
    auc_score = auc(fpr, tpr)

    return {
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "thresholds": thresholds.tolist(),
        "auc_score": round(auc_score, 4),
    }
