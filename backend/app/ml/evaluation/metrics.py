"""
Evaluation metrics calculator for Software Reliability ML pipeline.

Computes classification metrics plus software reliability statistics (MTBF, failure intensity, R(t)).
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
from typing import Dict, Any


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray = None,
) -> Dict[str, Any]:
    """
    Compute standard classification evaluation metrics.

    Returns:
        Dictionary with accuracy, precision, recall, f1_score, roc_auc, and classification_report.
    """
    metrics = {
        "accuracy": float(round(accuracy_score(y_true, y_pred), 4)),
        "precision": float(round(precision_score(y_true, y_pred, zero_division=0), 4)),
        "recall": float(round(recall_score(y_true, y_pred, zero_division=0), 4)),
        "f1_score": float(round(f1_score(y_true, y_pred, zero_division=0), 4)),
    }

    if y_proba is not None:
        metrics["roc_auc"] = float(round(roc_auc_score(y_true, y_proba), 4))
    else:
        metrics["roc_auc"] = 0.0

    metrics["classification_report"] = classification_report(
        y_true, y_pred, output_dict=True, zero_division=0
    )

    return metrics


def compute_reliability_statistics(
    failure_probability: float,
    operational_hours: float = 1000.0,
) -> Dict[str, Any]:
    """
    Compute Software Reliability Growth Model (SRGM) statistics.

    Uses Non-Homogeneous Poisson Process (NHPP) approximations:
        - Failure Intensity (λ): estimated from failure probability
        - MTBF: Mean Time Between Failures = 1/λ
        - R(t): Reliability Probability = e^(-λ * t)

    Args:
        failure_probability: Predicted probability of failure (0.0 - 1.0).
        operational_hours: Operational time window for R(t) calculation.

    Returns:
        Dictionary with failure_intensity, mtbf, reliability_probability, and reliability_score.
    """
    # Clamp failure probability to prevent division by zero / overflow
    fp = max(min(failure_probability, 0.999), 0.001)

    # Estimate failure intensity (failures per hour)
    # Using -ln(1 - fp) / t as NHPP approximation
    failure_intensity = -np.log(1.0 - fp) / operational_hours

    # Mean Time Between Failures
    mtbf = 1.0 / failure_intensity if failure_intensity > 0 else float("inf")

    # Reliability Probability: R(t) = e^(-λ * t)
    reliability_probability = np.exp(-failure_intensity * operational_hours)

    # Composite Reliability Score (0-100 scale)
    reliability_score = round((1.0 - fp) * 100.0, 2)

    return {
        "failure_intensity": round(failure_intensity, 8),
        "mtbf_hours": round(mtbf, 2),
        "reliability_probability": round(reliability_probability, 4),
        "reliability_score": reliability_score,
        "operational_hours": operational_hours,
    }
