"""
XGBoost Classifier for Software Reliability Prediction.
"""

try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None
from typing import Dict, Any, Optional


def create_xgboost(
    n_estimators: int = 200,
    max_depth: int = 6,
    learning_rate: float = 0.1,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    reg_alpha: float = 0.1,
    reg_lambda: float = 1.0,
    random_state: int = 42,
    scale_pos_weight: Optional[float] = None,
    **kwargs,
) -> XGBClassifier:
    """
    Create and return a configured XGBoost Classifier.

    Args:
        n_estimators: Number of boosting rounds.
        max_depth: Maximum tree depth.
        learning_rate: Step size shrinkage to prevent overfitting.
        subsample: Fraction of samples used per boosting round.
        colsample_bytree: Fraction of features used per tree.
        reg_alpha: L1 regularization term on weights.
        reg_lambda: L2 regularization term on weights.
        random_state: Random seed.
        scale_pos_weight: Controls balance for imbalanced classes.

    Returns:
        Configured XGBClassifier instance.
    """
    if XGBClassifier is None:
        raise RuntimeError("xgboost package is not installed in this environment.")
    params = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "learning_rate": learning_rate,
        "subsample": subsample,
        "colsample_bytree": colsample_bytree,
        "reg_alpha": reg_alpha,
        "reg_lambda": reg_lambda,
        "random_state": random_state,
        "eval_metric": "logloss",
        "n_jobs": 1,
    }

    if scale_pos_weight is not None:
        params["scale_pos_weight"] = scale_pos_weight

    params.update(kwargs)
    return XGBClassifier(**params)


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default hyperparameters for XGBoost."""
    return {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
    }


def get_tuning_grid() -> Dict[str, list]:
    """Return hyperparameter search grid for tuning."""
    return {
        "n_estimators": [100, 200, 300],
        "max_depth": [4, 6, 8, 10],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "subsample": [0.7, 0.8, 0.9],
        "colsample_bytree": [0.7, 0.8, 0.9],
    }
