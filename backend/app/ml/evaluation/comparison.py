"""
Model comparison utilities for Software Reliability ML pipeline.

Ranks all trained models by multiple metrics and selects the best candidate.
"""

import pandas as pd
from typing import List, Dict, Any


def compare_models(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare trained models by their evaluation metrics and rank them.

    Args:
        results: List of training result dicts from ModelTrainer.train_all_models().

    Returns:
        Dictionary with:
            - ranking: DataFrame sorted by F1 score
            - best_algorithm: name of the best model
            - best_metrics: metrics dict of the best model
    """
    rows = []
    for r in results:
        if r.get("model") is not None:
            row = {
                "algorithm": r["algorithm"],
                "training_time_sec": r["training_time"],
            }
            row.update(r["metrics"])
            rows.append(row)

    if not rows:
        return {
            "ranking": pd.DataFrame(),
            "best_algorithm": None,
            "best_metrics": None,
        }

    df = pd.DataFrame(rows)
    df = df.sort_values("f1_score", ascending=False).reset_index(drop=True)
    df.index = df.index + 1  # 1-indexed rank
    df.index.name = "rank"

    best = df.iloc[0]

    return {
        "ranking": df,
        "best_algorithm": best["algorithm"],
        "best_metrics": {
            "accuracy": best["accuracy"],
            "precision": best["precision"],
            "recall": best["recall"],
            "f1_score": best["f1_score"],
            "roc_auc": best["roc_auc"],
        },
    }
