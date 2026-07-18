"""
Decision Tree Classifier for Software Reliability Prediction.

Provides transparent, human-readable rule generation
(e.g., IF complexity > 20 AND coverage < 30 THEN Risk = HIGH).
"""

from sklearn.tree import DecisionTreeClassifier
from typing import Dict, Any, Optional


def create_decision_tree(
    max_depth: Optional[int] = 8,
    min_samples_split: int = 5,
    min_samples_leaf: int = 2,
    class_weight: str = "balanced",
    random_state: int = 42,
    **kwargs,
) -> DecisionTreeClassifier:
    """
    Create and return a configured Decision Tree Classifier.

    Args:
        max_depth: Maximum tree depth. None for unlimited.
        min_samples_split: Minimum samples to split an internal node.
        min_samples_leaf: Minimum samples at a leaf node.
        class_weight: 'balanced' auto-adjusts for class imbalance.
        random_state: Random seed.

    Returns:
        Configured DecisionTreeClassifier instance.
    """
    return DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        class_weight=class_weight,
        random_state=random_state,
        **kwargs,
    )


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default hyperparameters for Decision Tree."""
    return {
        "max_depth": 8,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "class_weight": "balanced",
    }


def get_tuning_grid() -> Dict[str, list]:
    """Return hyperparameter search grid for tuning."""
    return {
        "max_depth": [5, 8, 10, 15, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    }
