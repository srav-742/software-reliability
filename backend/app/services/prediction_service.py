"""
Prediction Service for Software Reliability.

Orchestrates inference: loads metrics from DB, runs ML prediction,
generates SHAP explanations, and persists results.
"""

import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.ml.inference.predictor import reliability_predictor
from app.ml.inference.postprocessing import classify_risk_level, generate_recommendations
from app.ml.explainability.shap_explainer import shap_explainer
from app.ml.explainability.feature_importance import get_feature_importance
from app.repositories.metrics_repository import metrics_repository
from app.repositories.prediction_repository import prediction_repository
from app.repositories.project_repository import project_repository
from app.ml.datasets.generate_dataset import FEATURE_COLUMNS


class PredictionService:
    """
    High-level prediction service that:
    1. Fetches project metrics from DB
    2. Runs ML inference
    3. Generates SHAP explanations
    4. Produces recommendations
    5. Persists prediction to DB
    """

    def predict_project(
        self,
        db: Session,
        project_id: int,
    ) -> Dict[str, Any]:
        """
        Run reliability prediction for a project.

        Requires:
            - Project must exist and have metrics (run /analyze first)
            - A trained model must exist on disk (run /train first)

        Returns:
            Prediction result with failure probability, risk level,
            reliability stats, and recommendations.
        """
        # 1. Get latest metrics for the project
        metric = metrics_repository.get_by_project(db, project_id=project_id)
        if not metric:
            raise ValueError(
                f"No metrics found for project {project_id}. "
                "Run analysis first via POST /api/v1/projects/{project_id}/analyze"
            )

        # 2. Build feature dict from DB metric
        features = {}
        for col in FEATURE_COLUMNS:
            features[col] = getattr(metric, col, 0)

        # 3. Run inference
        prediction = reliability_predictor.predict(features)

        # 4. Generate SHAP explanation
        shap_data = {}
        recommendations = []
        try:
            shap_result = shap_explainer.explain(features)
            shap_data = shap_result["shap_values"]

            # Generate recommendations from SHAP contributions
            recommendations = generate_recommendations(
                feature_contributions=shap_data,
                risk_level=prediction["risk_level"],
            )
        except Exception:
            # SHAP may fail for certain model types; gracefully degrade
            recommendations = generate_recommendations(
                feature_contributions={col: 0.0 for col in FEATURE_COLUMNS},
                risk_level=prediction["risk_level"],
            )

        # 5. Persist prediction to DB
        saved_prediction = prediction_repository.create(
            db,
            project_id=project_id,
            metric_id=metric.id,
            model_name=prediction["model_used"],
            failure_probability=prediction["failure_probability"],
            predicted_label=prediction["predicted_label"],
            risk_level=prediction["risk_level"],
            confidence_score=prediction["confidence_score"],
            shap_summary=shap_data,
            recommendations=recommendations,
        )

        return {
            "project_id": project_id,
            "predicted_label": prediction["predicted_label"],
            "failure_probability": prediction["failure_probability"],
            "risk_level": prediction["risk_level"],
            "confidence_score": prediction["confidence_score"],
            "reliability_stats": prediction["reliability_stats"],
            "model_used": prediction["model_used"],
            "recommendations": recommendations,
            "prediction_id": saved_prediction.id,
        }

    def explain_project(
        self,
        db: Session,
        project_id: int,
    ) -> Dict[str, Any]:
        """
        Get detailed SHAP explanation for a project's prediction.

        Returns:
            SHAP feature contributions, feature importance, and recommendations.
        """
        # Get latest metrics
        metric = metrics_repository.get_by_project(db, project_id=project_id)
        if not metric:
            raise ValueError(
                f"No metrics found for project {project_id}. "
                "Run analysis first."
            )

        features = {}
        for col in FEATURE_COLUMNS:
            features[col] = getattr(metric, col, 0)

        # SHAP explanation
        shap_result = shap_explainer.explain(features)

        # Feature importance
        importance = get_feature_importance()

        # Prediction for risk level
        prediction = reliability_predictor.predict(features)

        # Recommendations
        recommendations = generate_recommendations(
            feature_contributions=shap_result["shap_values"],
            risk_level=prediction["risk_level"],
        )

        return {
            "project_id": project_id,
            "model_used": prediction["model_used"],
            "top_risk_factors": shap_result["top_risk_factors"],
            "shap_values": shap_result["shap_values"],
            "feature_importance": importance["feature_importance"],
            "recommendations": recommendations,
        }


prediction_service = PredictionService()
