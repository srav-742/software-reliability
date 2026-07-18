"""
Confusion Matrix generation for Software Reliability evaluation.
"""

import numpy as np
from sklearn.metrics import confusion_matrix as sk_confusion_matrix
from typing import Dict, Any, List


def compute_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: List[int] = None,
) -> Dict[str, Any]:
    """
    Compute the confusion matrix and return as a structured dictionary.

    Returns:
        Dictionary with:
            - matrix: 2D list of confusion matrix values
            - true_negatives, false_positives, false_negatives, true_positives
            - total_samples
    """
    if labels is None:
        labels = [0, 1]

    cm = sk_confusion_matrix(y_true, y_pred, labels=labels)

    tn, fp, fn, tp = cm.ravel()

    return {
        "matrix": cm.tolist(),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "total_samples": int(tn + fp + fn + tp),
        "labels": labels,
    }
