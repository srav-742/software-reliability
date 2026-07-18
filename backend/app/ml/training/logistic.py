"""
Logistic Regression Classifier for Software Reliability Prediction.

Serves as the baseline benchmark model with interpretable log-odds coefficients.
"""

from sklearn.linear_model import LogisticRegression
from typing import Dict, Any


def create_logistic_regression(
    C: float = 1.0,
    max_iter: int = 1000,
    solver: str = "lbfgs",
    class_weight: str = "balanced",
    random_state: int = 42,
    **kwargs,
) -> LogisticRegression:
    """
    Create and return a configured Logistic Regression Classifier.

    Args:
        C: Inverse of regularization strength. Smaller values → stronger regularization.
        max_iter: Maximum iterations for solver convergence.
        solver: Algorithm for optimization ('lbfgs', 'liblinear', 'saga').
        class_weight: 'balanced' adjusts weights by class frequency.
        random_state: Random seed.

    Returns:
        Configured LogisticRegression instance.
    """
    return LogisticRegression(
        C=C,
        max_iter=max_iter,
        solver=solver,
        class_weight=class_weight,
        random_state=random_state,
        n_jobs=-1,
        **kwargs,
    )


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default hyperparameters for Logistic Regression."""
    return {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "class_weight": "balanced",
    }


def get_tuning_grid() -> Dict[str, list]:
    """Return hyperparameter search grid for tuning."""
    return {
        "C": [0.01, 0.1, 1.0, 10.0],
        "solver": ["lbfgs", "liblinear"],
    }
