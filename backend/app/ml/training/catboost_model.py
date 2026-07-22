"""
CatBoost Classifier for Software Reliability Prediction.
"""

try:
    from catboost import CatBoostClassifier
except ImportError:
    CatBoostClassifier = None
from typing import Dict, Any, Optional


def create_catboost(
    iterations: int = 200,
    depth: int = 6,
    learning_rate: float = 0.1,
    l2_leaf_reg: float = 3.0,
    random_state: int = 42,
    auto_class_weights: str = "Balanced",
    **kwargs,
) -> CatBoostClassifier:
    """
    Create and return a configured CatBoost Classifier.

    Args:
        iterations: Number of boosting iterations.
        depth: Depth of each tree.
        learning_rate: Step size shrinkage.
        l2_leaf_reg: L2 regularization coefficient.
        random_state: Random seed.
        auto_class_weights: 'Balanced' automatically adjusts for class imbalance.

    Returns:
        Configured CatBoostClassifier instance.
    """
    if CatBoostClassifier is None:
        raise RuntimeError("catboost package is not installed in this environment.")
    return CatBoostClassifier(
        iterations=iterations,
        depth=depth,
        learning_rate=learning_rate,
        l2_leaf_reg=l2_leaf_reg,
        random_state=random_state,
        auto_class_weights=auto_class_weights,
        verbose=0,
        **kwargs,
    )


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default hyperparameters for CatBoost."""
    return {
        "iterations": 200,
        "depth": 6,
        "learning_rate": 0.1,
        "l2_leaf_reg": 3.0,
        "auto_class_weights": "Balanced",
    }


def get_tuning_grid() -> Dict[str, list]:
    """Return hyperparameter search grid for tuning."""
    return {
        "iterations": [100, 200, 300],
        "depth": [4, 6, 8, 10],
        "learning_rate": [0.01, 0.05, 0.1],
        "l2_leaf_reg": [1.0, 3.0, 5.0, 7.0],
    }
