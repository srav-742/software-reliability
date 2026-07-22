"""
LightGBM Classifier for Software Reliability Prediction.
"""

try:
    from lightgbm import LGBMClassifier
except ImportError:
    LGBMClassifier = None
from typing import Dict, Any, Optional


def create_lightgbm(
    n_estimators: int = 200,
    max_depth: int = -1,
    learning_rate: float = 0.1,
    num_leaves: int = 31,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    reg_alpha: float = 0.1,
    reg_lambda: float = 1.0,
    random_state: int = 42,
    is_unbalance: bool = True,
    **kwargs,
) -> LGBMClassifier:
    """
    Create and return a configured LightGBM Classifier.

    Args:
        n_estimators: Number of boosting iterations.
        max_depth: Maximum tree depth. -1 means no limit.
        learning_rate: Boosting learning rate.
        num_leaves: Maximum number of leaves in one tree (leaf-wise growth).
        subsample: Fraction of data used per iteration.
        colsample_bytree: Fraction of features used per tree.
        reg_alpha: L1 regularization.
        reg_lambda: L2 regularization.
        random_state: Random seed.
        is_unbalance: Automatically handle imbalanced datasets.

    Returns:
        Configured LGBMClassifier instance.
    """
    if LGBMClassifier is None:
        raise RuntimeError("lightgbm package is not installed in this environment.")
    return LGBMClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        random_state=random_state,
        is_unbalance=is_unbalance,
        n_jobs=1,
        verbose=-1,
        **kwargs,
    )


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default hyperparameters for LightGBM."""
    return {
        "n_estimators": 200,
        "max_depth": -1,
        "learning_rate": 0.1,
        "num_leaves": 31,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "is_unbalance": True,
    }


def get_tuning_grid() -> Dict[str, list]:
    """Return hyperparameter search grid for tuning."""
    return {
        "n_estimators": [100, 200, 300],
        "max_depth": [-1, 10, 20],
        "learning_rate": [0.01, 0.05, 0.1],
        "num_leaves": [15, 31, 63],
        "subsample": [0.7, 0.8, 0.9],
    }
