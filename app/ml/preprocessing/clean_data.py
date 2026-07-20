"""
Data cleaning utilities for Software Reliability ML pipeline.

Handles missing values, outlier capping, and data type validation.
"""

import pandas as pd
import numpy as np
from typing import List, Optional


def clean_dataframe(
    df: pd.DataFrame,
    feature_columns: Optional[List[str]] = None,
    cap_outliers: bool = True,
    percentile_lower: float = 1.0,
    percentile_upper: float = 99.0,
) -> pd.DataFrame:
    """
    Clean the input DataFrame.

    Steps:
        1. Drop rows with all NaN values.
        2. Fill remaining NaN with column median (numeric) or mode (categorical).
        3. Optionally cap outliers to specified percentile bounds.

    Args:
        df: Input dataframe.
        feature_columns: Specific columns to clean. If None, cleans all numeric columns.
        cap_outliers: Whether to cap extreme values using percentile winsorization.
        percentile_lower: Lower percentile bound for outlier capping.
        percentile_upper: Upper percentile bound for outlier capping.

    Returns:
        Cleaned DataFrame.
    """
    df = df.copy()

    # Drop rows that are entirely empty
    df.dropna(how="all", inplace=True)

    if feature_columns is None:
        feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    # Fill NaN with median for numeric columns
    for col in feature_columns:
        if col in df.columns and df[col].isna().any():
            df[col].fillna(df[col].median(), inplace=True)

    # Cap outliers using percentile winsorization
    if cap_outliers:
        for col in feature_columns:
            if col in df.columns and df[col].dtype in [np.float64, np.int64, np.float32, np.int32]:
                lower = np.percentile(df[col].dropna(), percentile_lower)
                upper = np.percentile(df[col].dropna(), percentile_upper)
                df[col] = df[col].clip(lower=lower, upper=upper)

    return df
