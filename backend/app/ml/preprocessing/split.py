"""
Train/Test split utilities for Software Reliability ML pipeline.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Tuple


def split_dataset(
    df: pd.DataFrame,
    target_column: str = "api_failure",
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split the dataset into training and test sets.

    Args:
        df: Full dataframe with features and target.
        target_column: Name of the target label column.
        test_size: Fraction of data to use for testing (0.0 - 1.0).
        random_state: Random seed for reproducibility.
        stratify: Whether to stratify split by target class distribution.

    Returns:
        (X_train, X_test, y_train, y_test)
    """
    feature_columns = [col for col in df.columns if col != target_column]

    X = df[feature_columns]
    y = df[target_column]

    stratify_col = y if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_col,
    )

    return X_train, X_test, y_train, y_test
