"""
Evaluation pipeline orchestrator for Software Reliability.
"""

from typing import Dict, Any
import numpy as np

from app.ml.evaluation.metrics import compute_classification_metrics, compute_reliability_statistics
from app.ml.evaluation.confusion_matrix import compute_confusion_matrix
from app.ml.evaluation.roc_auc import compute_roc_curve


def run_evaluation_pipeline(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray = None,
) -> Dict[str, Any]:
    """
    Run full evaluation pipeline on model predictions.

    Returns classification metrics, confusion matrix, and ROC curve data.
    """
    # Classification metrics
    metrics = compute_classification_metrics(y_true, y_pred, y_proba)

    # Confusion matrix
    cm = compute_confusion_matrix(y_true, y_pred)

    # ROC curve
    roc = None
    if y_proba is not None:
        roc = compute_roc_curve(y_true, y_proba)

    return {
        "metrics": metrics,
        "confusion_matrix": cm,
        "roc_curve": roc,
    }
