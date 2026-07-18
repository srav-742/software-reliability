"""
Trainer Orchestrator for Software Reliability ML Pipeline.

Trains all 7 ML models, evaluates them, compares performance,
serializes the best model, and returns comprehensive results.
"""

import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from sklearn.ensemble import VotingClassifier

from app.ml.training.random_forest import create_random_forest
from app.ml.training.xgboost_model import create_xgboost
from app.ml.training.lightgbm_model import create_lightgbm
from app.ml.training.catboost_model import create_catboost
from app.ml.training.svm import create_svm
from app.ml.training.decision_tree import create_decision_tree
from app.ml.training.logistic import create_logistic_regression


def create_voting_ensemble():
    """Create a soft-voting ensemble combining XGBoost, CatBoost, and Random Forest."""
    return VotingClassifier(
        estimators=[
            ("xgb", create_xgboost()),
            ("cat", create_catboost(iterations=100)),
            ("rf", create_random_forest()),
        ],
        voting="soft",
    )


# Directory to save trained models
SAVED_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "saved_models"
)


# Registry mapping algorithm name → factory function
MODEL_REGISTRY = {
    "voting_ensemble": create_voting_ensemble,
    "random_forest": create_random_forest,
    "xgboost": create_xgboost,
    "lightgbm": create_lightgbm,
    "catboost": create_catboost,
    "svm": create_svm,
    "decision_tree": create_decision_tree,
    "logistic_regression": create_logistic_regression,
}


class ModelTrainer:
    """
    Trains all registered ML models, evaluates on test data,
    selects the best model by F1 score, and persists it to disk.
    """

    def __init__(self, save_dir: Optional[str] = None):
        self.save_dir = save_dir or os.path.abspath(SAVED_MODELS_DIR)
        os.makedirs(self.save_dir, exist_ok=True)

    def train_single_model(
        self,
        algorithm: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        tune: bool = True,
    ) -> Dict[str, Any]:
        """
        Train a single model (optionally with hyperparameter tuning) and evaluate on test data.

        Returns:
            Dictionary with model object, algorithm name, evaluation metrics, and training time.
        """
        if algorithm not in MODEL_REGISTRY:
            raise ValueError(f"Unknown algorithm: {algorithm}. Available: {list(MODEL_REGISTRY.keys())}")

        factory = MODEL_REGISTRY[algorithm]
        model = factory()

        compact_grids = {
            "random_forest": {
                "n_estimators": [100, 300],
                "max_depth": [10, 20, None],
            },
            "xgboost": {
                "n_estimators": [100, 300],
                "max_depth": [6, 10, 14],
                "learning_rate": [0.05, 0.1, 0.2],
            },
            "lightgbm": {
                "n_estimators": [100, 300],
                "num_leaves": [31, 63, 127],
                "learning_rate": [0.05, 0.1, 0.2],
            },
            "catboost": {
                "iterations": [150, 300],
                "depth": [6, 8, 10],
            },
            "svm": {
                "C": [1.0, 10.0, 100.0],
                "kernel": ["rbf", "linear"],
            },
            "decision_tree": {
                "max_depth": [10, 20, None],
            },
            "logistic_regression": {
                "C": [1.0, 10.0, 100.0],
            },
        }

        # Train
        start_time = time.time()
        if tune and algorithm in compact_grids:
            from app.ml.training.hyperparameter_tuning import tune_model
            grid = compact_grids[algorithm]
            tuned_model, best_params, _ = tune_model(
                model=model,
                param_grid=grid,
                X_train=X_train,
                y_train=y_train,
                cv=3,  # 3-fold for speed
                scoring="f1",
                n_jobs=1,
            )
            model = tuned_model
        else:
            model.fit(X_train, y_train)
        training_time = round(time.time() - start_time, 4)

        # Predict
        y_pred = model.predict(X_test)

        # Probability scores (for ROC-AUC)
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = y_pred.astype(float)

        # Evaluate
        metrics = {
            "accuracy": float(round(accuracy_score(y_test, y_pred), 4)),
            "precision": float(round(precision_score(y_test, y_pred, zero_division=0), 4)),
            "recall": float(round(recall_score(y_test, y_pred, zero_division=0), 4)),
            "f1_score": float(round(f1_score(y_test, y_pred, zero_division=0), 4)),
            "roc_auc": float(round(roc_auc_score(y_test, y_proba), 4)),
        }

        return {
            "algorithm": algorithm,
            "model": model,
            "metrics": metrics,
            "training_time": training_time,
        }

    def train_all_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        algorithms: Optional[List[str]] = None,
        tune: bool = True,
    ) -> Dict[str, Any]:
        """
        Train all (or specified) models and return comparison results.

        Args:
            X_train: Scaled training features.
            y_train: Training labels.
            X_test: Scaled test features.
            y_test: Test labels.
            algorithms: List of algorithm names to train. None trains all.
            tune: Whether to perform hyperparameter tuning.

        Returns:
            Dictionary with:
                - results: list of per-model results
                - best_model: the best performing model result
                - comparison_df: DataFrame of all model metrics
        """
        if algorithms is None:
            algorithms = list(MODEL_REGISTRY.keys())

        results = []
        for algo in algorithms:
            try:
                result = self.train_single_model(algo, X_train, y_train, X_test, y_test, tune=tune)
                results.append(result)
            except Exception as e:
                results.append({
                    "algorithm": algo,
                    "model": None,
                    "metrics": {
                        "accuracy": 0.0,
                        "precision": 0.0,
                        "recall": 0.0,
                        "f1_score": 0.0,
                        "roc_auc": 0.0,
                    },
                    "training_time": 0.0,
                    "error": str(e),
                })

        # Sort by F1 score descending
        valid_results = [r for r in results if r.get("model") is not None]
        if valid_results:
            best_result = max(valid_results, key=lambda r: r["metrics"]["f1_score"])
        else:
            best_result = results[0] if results else None

        # Build comparison DataFrame
        comparison_rows = []
        for r in results:
            row = {"algorithm": r["algorithm"], "training_time": r["training_time"]}
            row.update(r["metrics"])
            if "error" in r:
                row["error"] = r["error"]
            comparison_rows.append(row)

        comparison_df = pd.DataFrame(comparison_rows)

        return {
            "results": results,
            "best_model": best_result,
            "comparison_df": comparison_df,
        }

    def save_best_model(
        self,
        model,
        scaler,
        algorithm: str,
        metrics: Dict[str, float],
        feature_columns: List[str],
    ) -> Dict[str, str]:
        """
        Persist the best model, scaler, and metadata to disk.

        Returns:
            Dictionary of saved file paths.
        """
        model_path = os.path.join(self.save_dir, "best_model.pkl")
        scaler_path = os.path.join(self.save_dir, "scaler.pkl")
        metadata_path = os.path.join(self.save_dir, "metadata.json")

        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)

        metadata = {
            "algorithm": algorithm,
            "metrics": metrics,
            "feature_columns": feature_columns,
            "version": "1.0",
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return {
            "model_path": model_path,
            "scaler_path": scaler_path,
            "metadata_path": metadata_path,
        }
