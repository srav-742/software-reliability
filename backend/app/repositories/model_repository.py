"""
Repository for ModelRegistry database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.model_registry import ModelRegistry


class ModelRegistryRepository:
    """CRUD operations for ModelRegistry records."""

    def create(self, db: Session, **kwargs) -> ModelRegistry:
        """Create or update a model registry entry."""
        db_obj = ModelRegistry(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: int) -> Optional[ModelRegistry]:
        """Get a model by ID."""
        return db.query(ModelRegistry).filter(ModelRegistry.id == id).first()

    def get_by_name(self, db: Session, *, model_name: str) -> Optional[ModelRegistry]:
        """Get a model by name."""
        return db.query(ModelRegistry).filter(ModelRegistry.model_name == model_name).first()

    def get_active_model(self, db: Session) -> Optional[ModelRegistry]:
        """Get the currently active model."""
        return (
            db.query(ModelRegistry)
            .filter(ModelRegistry.is_active == True)
            .order_by(ModelRegistry.created_at.desc())
            .first()
        )

    def list_all(self, db: Session, skip: int = 0, limit: int = 50) -> List[ModelRegistry]:
        """List all registered models."""
        return (
            db.query(ModelRegistry)
            .order_by(ModelRegistry.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def deactivate_all(self, db: Session) -> None:
        """Deactivate all models (used before setting a new active model)."""
        db.query(ModelRegistry).update({ModelRegistry.is_active: False})
        db.commit()

    def set_active(self, db: Session, *, model_id: int) -> Optional[ModelRegistry]:
        """Set a specific model as active (deactivates all others first)."""
        self.deactivate_all(db)
        model = self.get(db, id=model_id)
        if model:
            model.is_active = True
            db.commit()
            db.refresh(model)
        return model


model_repository = ModelRegistryRepository()
