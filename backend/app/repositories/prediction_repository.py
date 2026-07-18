"""
Repository for Prediction database operations.
"""

import json
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.prediction import Prediction


class PredictionRepository:
    """CRUD operations for Prediction records."""

    def create(
        self,
        db: Session,
        *,
        project_id: int,
        metric_id: int,
        model_name: str,
        failure_probability: float,
        predicted_label: int,
        risk_level: str,
        confidence_score: float,
        shap_summary: Optional[dict] = None,
        recommendations: Optional[list] = None,
    ) -> Prediction:
        """Create a new prediction record."""
        db_obj = Prediction(
            project_id=project_id,
            metric_id=metric_id,
            model_name=model_name,
            failure_probability=failure_probability,
            predicted_label=predicted_label,
            risk_level=risk_level,
            confidence_score=confidence_score,
            shap_summary=json.dumps(shap_summary) if shap_summary else None,
            recommendations=json.dumps(recommendations) if recommendations else None,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: int) -> Optional[Prediction]:
        """Get a prediction by ID."""
        return db.query(Prediction).filter(Prediction.id == id).first()

    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 50
    ) -> List[Prediction]:
        """Get all predictions for a project."""
        return (
            db.query(Prediction)
            .filter(Prediction.project_id == project_id)
            .order_by(Prediction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_by_project(
        self, db: Session, *, project_id: int
    ) -> Optional[Prediction]:
        """Get the most recent prediction for a project."""
        return (
            db.query(Prediction)
            .filter(Prediction.project_id == project_id)
            .order_by(Prediction.created_at.desc())
            .first()
        )


prediction_repository = PredictionRepository()
