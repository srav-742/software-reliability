"""
Hyperparameter tuning module using GridSearchCV for Software Reliability models.
"""

import numpy as np
from sklearn.model_selection import GridSearchCV
from typing import Dict, Any, Tuple


def tune_model(
    model,
    param_grid: Dict[str, list],
    X_train: np.ndarray,
    y_train: np.ndarray,
    cv: int = 5,
    scoring: str = "f1",
    n_jobs: int = -1,
) -> Tuple[Any, Dict[str, Any], float]:
    """
    Perform Grid Search Cross-Validation to find optimal hyperparameters.

    Args:
        model: Unfitted sklearn-compatible estimator.
        param_grid: Dictionary of hyperparameters to search.
        X_train: Scaled training features.
        y_train: Training labels.
        cv: Number of cross-validation folds.
        scoring: Scoring metric to optimize ('f1', 'accuracy', 'roc_auc').
        n_jobs: Number of parallel jobs.

    Returns:
        (best_model, best_params, best_score)
    """
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=n_jobs,
        verbose=0,
        refit=True,
    )

    grid_search.fit(X_train, y_train)

    return (
        grid_search.best_estimator_,
        grid_search.best_params_,
        grid_search.best_score_,
    )
