"""
Training pipeline orchestrator for Software Reliability.

Chains preprocessing → training → evaluation into a single callable.
"""

from typing import Dict, Any, Optional, List

from app.ml.preprocessing.preprocessing_pipeline import PreprocessingPipeline
from app.ml.training.trainer import ModelTrainer
from app.ml.evaluation.comparison import compare_models


def run_training_pipeline(
    dataset_path: Optional[str] = None,
    algorithms: Optional[List[str]] = None,
    test_size: float = 0.2,
) -> Dict[str, Any]:
    """
    Execute the full training pipeline standalone (without DB).

    Returns:
        Dictionary with preprocessing results, training results,
        and comparison summary.
    """
    # 1. Preprocess
    pipeline = PreprocessingPipeline()
    prep_result = pipeline.run(csv_path=dataset_path, test_size=test_size)

    # 2. Train
    trainer = ModelTrainer()
    train_result = trainer.train_all_models(
        prep_result["X_train_scaled"],
        prep_result["y_train"].values,
        prep_result["X_test_scaled"],
        prep_result["y_test"].values,
        algorithms=algorithms,
    )

    # 3. Compare
    comparison = compare_models(train_result["results"])

    # 4. Save best
    best = train_result["best_model"]
    model_paths = {}
    if best and best.get("model") is not None:
        model_paths = trainer.save_best_model(
            model=best["model"],
            scaler=prep_result["scaler"].scaler,
            algorithm=best["algorithm"],
            metrics=best["metrics"],
            feature_columns=prep_result["feature_columns"],
        )

    return {
        "dataset_size": prep_result["dataset_size"],
        "best_algorithm": comparison["best_algorithm"],
        "best_metrics": comparison["best_metrics"],
        "comparison": comparison["ranking"].to_dict("records") if not comparison["ranking"].empty else [],
        "model_paths": model_paths,
    }
