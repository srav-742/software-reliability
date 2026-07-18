"""
Random Forest Classifier for Software Reliability Prediction.
"""

from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any, Optional
import numpy as np


def create_random_forest(
    n_estimators: int = 200,
    max_depth: Optional[int] = 15,
    min_samples_split: int = 5,
    min_samples_leaf: int = 2,
    random_state: int = 42,
    class_weight: str = "balanced",
    **kwargs,
) -> RandomForestClassifier:
    """
    Create and return a configured Random Forest Classifier.

    Args:
        n_estimators: Number of trees in the forest.
        max_depth: Maximum depth of each tree. None for unlimited.
        min_samples_split: Minimum samples required to split an internal node.
        min_samples_leaf: Minimum samples required at a leaf node.
        random_state: Random seed for reproducibility.
        class_weight: Handles imbalanced classes. 'balanced' adjusts weights inversely to class frequencies.

    Returns:
        Configured RandomForestClassifier instance.
    """
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        class_weight=class_weight,
        n_jobs=1,
        **kwargs,
    )


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default hyperparameters for Random Forest."""
    return {
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "class_weight": "balanced",
    }


def get_tuning_grid() -> Dict[str, list]:
    """Return hyperparameter search grid for tuning."""
    return {
        "n_estimators": [100, 200, 300],
        "max_depth": [10, 15, 20, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    }
