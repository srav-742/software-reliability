"""
Feature building utilities for Software Reliability ML pipeline.

Creates derived features from raw extracted code metrics.
"""

import pandas as pd
import numpy as np


def build_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features from raw code metrics.

    Adds:
        - complexity_per_function: cyclomatic_complexity / number_of_functions
        - params_per_function: number_of_parameters / number_of_functions
        - loc_per_function: lines_of_code / number_of_functions
        - external_dependency_ratio: (external_api_calls + database_queries) / lines_of_code
    """
    df = df.copy()

    # Avoid division by zero
    safe_functions = df["number_of_functions"].replace(0, 1)
    safe_loc = df["lines_of_code"].replace(0, 1)

    df["complexity_per_function"] = (df["cyclomatic_complexity"] / safe_functions).round(4)
    df["params_per_function"] = (df["number_of_parameters"] / safe_functions).round(4)
    df["loc_per_function"] = (df["lines_of_code"] / safe_functions).round(4)
    df["external_dependency_ratio"] = (
        (df["external_api_calls"] + df["database_queries"]) / safe_loc
    ).round(6)
    df["untested_complexity"] = (
        (df["cyclomatic_complexity"] / 80.0) * (1.0 - df["test_coverage"] / 100.0)
    ).round(4)
    df["duplication_depth"] = (
        (df["duplicate_code_score"] / 0.8) * (df["nested_depth"] / 12.0)
    ).round(4)
    df["resource_intensity"] = (
        (df["cpu_usage"] * df["memory_usage"]) / 10000.0
    ).round(4)

    # Composite reliability risk index
    loc_ratio = (df["lines_of_code"] / 5000.0) / ((df["number_of_functions"] / 100.0) + 0.01)
    df["composite_risk_index"] = (
        0.25 * df["untested_complexity"]
        + 0.20 * df["duplication_depth"]
        + 0.15 * (df["cyclomatic_complexity"] / 80.0)
        + 0.10 * np.clip(loc_ratio, 0, 2.0)
        + 0.10 * (df["historical_bug_count"] / 50.0)
        + 0.05 * (df["dependency_count"] / 30.0)
        + 0.05 * (df["average_response_time"] / 5000.0)
        + 0.05 * (df["cpu_usage"] / 95.0)
        + 0.05 * (df["memory_usage"] / 2048.0)
    ).round(6)

    return df
