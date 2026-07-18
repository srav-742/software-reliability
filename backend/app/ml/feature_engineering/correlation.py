"""
Correlation analysis for Software Reliability feature engineering.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlation matrix for numeric features."""
    numeric_df = df.select_dtypes(include=[np.number])
    return numeric_df.corr()


def find_highly_correlated(
    df: pd.DataFrame, threshold: float = 0.85
) -> List[Dict[str, Any]]:
    """
    Find feature pairs with absolute correlation above threshold.

    Returns list of dicts with feature1, feature2, and correlation value.
    """
    corr = compute_correlation_matrix(df)
    pairs = []

    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            val = corr.iloc[i, j]
            if abs(val) > threshold:
                pairs.append({
                    "feature1": corr.columns[i],
                    "feature2": corr.columns[j],
                    "correlation": round(val, 4),
                })

    return sorted(pairs, key=lambda x: abs(x["correlation"]), reverse=True)
