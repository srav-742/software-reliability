"""
Model Service for Software Reliability.

Provides model registry lookup and active model management.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories.model_repository import model_repository
from app.ml.inference.model_loader import is_model_available


class ModelService:
    """Service for querying and managing registered ML models."""

    def list_models(self, db: Session) -> List[Dict[str, Any]]:
        """List all registered models with their metrics."""
        models = model_repository.list_all(db)
        return [
            {
                "id": m.id,
                "model_name": m.model_name,
                "algorithm": m.algorithm,
                "version": m.version,
                "accuracy": m.accuracy,
                "precision": m.precision,
                "recall": m.recall,
                "f1_score": m.f1_score,
                "roc_auc": m.roc_auc,
                "framework": m.framework,
                "description": m.description,
                "is_active": m.is_active,
                "created_at": str(m.created_at) if m.created_at else None,
            }
            for m in models
        ]

    def get_active_model(self, db: Session) -> Optional[Dict[str, Any]]:
        """Get the currently active model."""
        model = model_repository.get_active_model(db)
        if not model:
            return None
        return {
            "id": model.id,
            "model_name": model.model_name,
            "algorithm": model.algorithm,
            "version": model.version,
            "accuracy": model.accuracy,
            "precision": model.precision,
            "recall": model.recall,
            "f1_score": model.f1_score,
            "roc_auc": model.roc_auc,
            "is_active": model.is_active,
            "model_available_on_disk": is_model_available(),
        }

    def set_active_model(self, db: Session, model_id: int) -> Optional[Dict[str, Any]]:
        """Set a model as the active inference model."""
        model = model_repository.set_active(db, model_id=model_id)
        if not model:
            return None
        return {
            "id": model.id,
            "model_name": model.model_name,
            "algorithm": model.algorithm,
            "is_active": model.is_active,
        }


model_service = ModelService()
