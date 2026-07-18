"""
Feature selection utilities for Software Reliability ML pipeline.
"""

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from typing import List, Tuple


def select_k_best_features(
    X: pd.DataFrame,
    y: pd.Series,
    k: int = 10,
) -> Tuple[List[str], np.ndarray]:
    """
    Select top-k features using ANOVA F-test.

    Returns:
        Tuple of (selected feature names, f-scores).
    """
    selector = SelectKBest(score_func=f_classif, k=min(k, X.shape[1]))
    selector.fit(X, y)

    selected_mask = selector.get_support()
    selected_features = X.columns[selected_mask].tolist()
    f_scores = selector.scores_

    return selected_features, f_scores
