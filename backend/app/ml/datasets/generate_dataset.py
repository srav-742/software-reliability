"""
Synthetic Dataset Generator for Software Reliability Model Training.

Generates a realistic dataset modeled on NASA MDP / PROMISE software defect
prediction datasets, using the same feature columns as our ApiMetric DB model.
"""

import os
import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "lines_of_code",
    "cyclomatic_complexity",
    "number_of_functions",
    "number_of_parameters",
    "nested_depth",
    "if_statement_count",
    "loop_count",
    "imports_count",
    "dependency_count",
    "duplicate_code_score",
    "exception_handling_count",
    "database_queries",
    "external_api_calls",
    "cpu_usage",
    "memory_usage",
    "average_response_time",
    "test_coverage",
    "historical_bug_count",
]

TARGET_COLUMN = "api_failure"


def generate_synthetic_dataset(n_samples: int = 3000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic software reliability dataset.

    The failure label is computed from a realistic heuristic:
    high complexity + low coverage + high duplication → higher failure probability.
    """
    rng = np.random.RandomState(seed)

    data = {
        "lines_of_code": rng.randint(20, 5000, n_samples),
        "cyclomatic_complexity": rng.randint(1, 80, n_samples),
        "number_of_functions": rng.randint(1, 100, n_samples),
        "number_of_parameters": rng.randint(0, 200, n_samples),
        "nested_depth": rng.randint(1, 12, n_samples),
        "if_statement_count": rng.randint(0, 60, n_samples),
        "loop_count": rng.randint(0, 40, n_samples),
        "imports_count": rng.randint(1, 50, n_samples),
        "dependency_count": rng.randint(0, 30, n_samples),
        "duplicate_code_score": rng.uniform(0.0, 0.8, n_samples).round(3),
        "exception_handling_count": rng.randint(0, 20, n_samples),
        "database_queries": rng.randint(0, 25, n_samples),
        "external_api_calls": rng.randint(0, 15, n_samples),
        "cpu_usage": rng.uniform(1.0, 95.0, n_samples).round(2),
        "memory_usage": rng.uniform(32.0, 2048.0, n_samples).round(2),
        "average_response_time": rng.uniform(10.0, 5000.0, n_samples).round(2),
        "test_coverage": rng.uniform(0.0, 100.0, n_samples).round(2),
        "historical_bug_count": rng.randint(0, 50, n_samples),
    }

    df = pd.DataFrame(data)

    # ---------------------------------------------------------------
    # Compute realistic failure label using non-linear risk score
    # ---------------------------------------------------------------
    untested_complexity = (df["cyclomatic_complexity"] / 80.0) * (1.0 - df["test_coverage"] / 100.0)
    duplication_depth = (df["duplicate_code_score"] / 0.8) * (df["nested_depth"] / 12.0)
    loc_per_func = (df["lines_of_code"] / 5000.0) / ((df["number_of_functions"] / 100.0) + 0.01)

    risk_score = (
        0.25 * untested_complexity
        + 0.20 * duplication_depth
        + 0.15 * (df["cyclomatic_complexity"] / 80.0)
        + 0.10 * np.clip(loc_per_func, 0, 2.0)
        + 0.10 * (df["historical_bug_count"] / 50.0)
        + 0.05 * (df["dependency_count"] / 30.0)
        + 0.05 * (df["average_response_time"] / 5000.0)
        + 0.05 * (df["cpu_usage"] / 95.0)
        + 0.05 * (df["memory_usage"] / 2048.0)
    )

    # Deterministic ground truth without artificial noise
    noise = 0.0
    risk_score = risk_score + noise

    # Threshold for failure: ~30% failure rate
    threshold = np.percentile(risk_score, 70)
    df[TARGET_COLUMN] = (risk_score >= threshold).astype(int)

    return df


def save_dataset(df: pd.DataFrame, filename: str = "synthetic_reliability_dataset.csv") -> str:
    """Save generated dataset to the datasets/raw directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(base_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    filepath = os.path.join(raw_dir, filename)
    df.to_csv(filepath, index=False)
    return filepath


if __name__ == "__main__":
    df = generate_synthetic_dataset(n_samples=1000)
    path = save_dataset(df)
    print(f"Dataset saved to: {path}")
    print(f"Shape: {df.shape}")
    print(f"Failure distribution:\n{df['api_failure'].value_counts()}")
