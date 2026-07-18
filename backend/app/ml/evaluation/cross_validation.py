"""
Cross-validation utilities for Software Reliability ML pipeline.
"""

import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold
from typing import Dict, Any


def perform_cross_validation(
    model,
    X: np.ndarray,
    y: np.ndarray,
    cv: int = 5,
    scoring: str = "f1",
) -> Dict[str, Any]:
    """
    Perform stratified k-fold cross-validation.

    Args:
        model: Sklearn-compatible estimator (unfitted).
        X: Feature matrix.
        y: Target labels.
        cv: Number of folds.
        scoring: Metric to evaluate ('f1', 'accuracy', 'roc_auc', 'precision', 'recall').

    Returns:
        Dictionary with mean score, std, individual fold scores, and fold count.
    """
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    scores = cross_val_score(model, X, y, cv=skf, scoring=scoring, n_jobs=-1)

    return {
        "scoring_metric": scoring,
        "n_folds": cv,
        "fold_scores": [round(s, 4) for s in scores.tolist()],
        "mean_score": round(np.mean(scores), 4),
        "std_score": round(np.std(scores), 4),
    }
