"""
Support Vector Machine (SVM) Classifier for Software Reliability Prediction.
"""

from sklearn.svm import SVC
from typing import Dict, Any


def create_svm(
    kernel: str = "rbf",
    C: float = 1.0,
    gamma: str = "scale",
    class_weight: str = "balanced",
    probability: bool = True,
    random_state: int = 42,
    **kwargs,
) -> SVC:
    """
    Create and return a configured SVM Classifier.

    Args:
        kernel: Kernel type ('rbf', 'linear', 'poly', 'sigmoid').
        C: Regularization parameter. Higher C → less regularization.
        gamma: Kernel coefficient. 'scale' uses 1/(n_features * X.var()).
        class_weight: 'balanced' adjusts weights by class frequency.
        probability: Enable probability estimates (required for predict_proba).
        random_state: Random seed.

    Returns:
        Configured SVC instance.
    """
    return SVC(
        kernel=kernel,
        C=C,
        gamma=gamma,
        class_weight=class_weight,
        probability=probability,
        random_state=random_state,
        **kwargs,
    )


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default hyperparameters for SVM."""
    return {
        "kernel": "rbf",
        "C": 1.0,
        "gamma": "scale",
        "class_weight": "balanced",
    }


def get_tuning_grid() -> Dict[str, list]:
    """Return hyperparameter search grid for tuning."""
    return {
        "kernel": ["rbf", "linear"],
        "C": [0.1, 1.0, 10.0],
        "gamma": ["scale", "auto"],
    }
