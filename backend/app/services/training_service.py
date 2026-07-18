"""
Training Service for Software Reliability ML Pipeline.

Orchestrates the full training workflow: preprocessing, training all models,
evaluation, model selection, persistence, and DB record creation.
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.ml.preprocessing.preprocessing_pipeline import PreprocessingPipeline
from app.ml.training.trainer import ModelTrainer
from app.ml.evaluation.comparison import compare_models
from app.repositories.training_repository import training_repository
from app.repositories.model_repository import model_repository


class TrainingService:
    """
    High-level service orchestrating model training, evaluation,
    persistence, and database record creation.
    """

    def __init__(self):
        self.pipeline = PreprocessingPipeline()
        self.trainer = ModelTrainer()

    def run_training(
        self,
        db: Session,
        user_id: int,
        algorithms: Optional[List[str]] = None,
        dataset_path: Optional[str] = None,
        test_size: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Execute the full training pipeline.

        Steps:
            1. Preprocess data (load/generate → clean → split → scale)
            2. Train all specified models
            3. Compare and select best model
            4. Save best model to disk
            5. Record training runs in DB
            6. Register best model in model_registry

        Returns:
            Dictionary with training results, best model info, and model paths.
        """
        # 1. Preprocess
        prep_result = self.pipeline.run(
            csv_path=dataset_path,
            test_size=test_size,
        )

        X_train = prep_result["X_train_scaled"]
        X_test = prep_result["X_test_scaled"]
        y_train = prep_result["y_train"]
        y_test = prep_result["y_test"]
        scaler = prep_result["scaler"]
        feature_columns = prep_result["feature_columns"]
        dataset_size = prep_result["dataset_size"]

        # 2. Train all models
        train_result = self.trainer.train_all_models(
            X_train, y_train.values, X_test, y_test.values,
            algorithms=algorithms,
        )

        results = train_result["results"]
        best_result = train_result["best_model"]

        # 3. Compare
        comparison = compare_models(results)

        # 4. Save best model to disk
        model_paths = {}
        if best_result and best_result.get("model") is not None:
            model_paths = self.trainer.save_best_model(
                model=best_result["model"],
                scaler=scaler.scaler,
                algorithm=best_result["algorithm"],
                metrics=best_result["metrics"],
                feature_columns=feature_columns,
            )

        # 5. Record training runs in DB
        all_results = []
        for r in results:
            is_best = (
                best_result is not None
                and r["algorithm"] == best_result["algorithm"]
            )

            hyperparams_str = json.dumps({"default": True})

            training_run = training_repository.create(
                db,
                user_id=user_id,
                algorithm=r["algorithm"],
                dataset_name=dataset_path or "synthetic_reliability_dataset",
                dataset_size=dataset_size,
                accuracy=r["metrics"]["accuracy"],
                precision=r["metrics"]["precision"],
                recall=r["metrics"]["recall"],
                f1_score=r["metrics"]["f1_score"],
                roc_auc=r["metrics"]["roc_auc"],
                training_time=r["training_time"],
                hyperparameters=hyperparams_str,
                model_path=model_paths.get("model_path", ""),
                is_best_model=is_best,
                status="Completed" if r.get("model") else "Failed",
            )

            all_results.append({
                "algorithm": r["algorithm"],
                "metrics": r["metrics"],
                "training_time": r["training_time"],
                "error": r.get("error"),
                "db_id": training_run.id,
            })

        # 6. Register best model in model_registry
        if best_result and best_result.get("model") is not None:
            # Deactivate previous models
            model_repository.deactivate_all(db)

            # Check if entry already exists
            existing = model_repository.get_by_name(
                db, model_name=f"reliability_{best_result['algorithm']}"
            )
            if existing:
                existing.accuracy = best_result["metrics"]["accuracy"]
                existing.precision = best_result["metrics"]["precision"]
                existing.recall = best_result["metrics"]["recall"]
                existing.f1_score = best_result["metrics"]["f1_score"]
                existing.roc_auc = best_result["metrics"]["roc_auc"]
                existing.model_path = model_paths.get("model_path", "")
                existing.scaler_path = model_paths.get("scaler_path", "")
                existing.is_active = True
                existing.version = "1.0"
                db.commit()
                db.refresh(existing)
            else:
                model_repository.create(
                    db,
                    model_name=f"reliability_{best_result['algorithm']}",
                    algorithm=best_result["algorithm"],
                    version="1.0",
                    model_path=model_paths.get("model_path", ""),
                    scaler_path=model_paths.get("scaler_path", ""),
                    accuracy=best_result["metrics"]["accuracy"],
                    precision=best_result["metrics"]["precision"],
                    recall=best_result["metrics"]["recall"],
                    f1_score=best_result["metrics"]["f1_score"],
                    roc_auc=best_result["metrics"]["roc_auc"],
                    framework="scikit-learn",
                    description=f"Best model selected from {len(results)} algorithms. "
                                f"Algorithm: {best_result['algorithm']}",
                    is_active=True,
                )

        return {
            "status": "success",
            "message": f"Training completed. Best model: {best_result['algorithm'] if best_result else 'none'}",
            "dataset_size": dataset_size,
            "best_algorithm": best_result["algorithm"] if best_result else None,
            "best_metrics": best_result["metrics"] if best_result else None,
            "all_results": all_results,
            "model_paths": model_paths,
        }


training_service = TrainingService()
