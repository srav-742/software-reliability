"""
Repository for TrainingRun database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.training import TrainingRun


class TrainingRepository:
    """CRUD operations for TrainingRun records."""

    def create(self, db: Session, **kwargs) -> TrainingRun:
        """Create a new training run record."""
        db_obj = TrainingRun(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: int) -> Optional[TrainingRun]:
        """Get a training run by ID."""
        return db.query(TrainingRun).filter(TrainingRun.id == id).first()

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[TrainingRun]:
        """Get all training runs for a user."""
        return (
            db.query(TrainingRun)
            .filter(TrainingRun.user_id == user_id)
            .order_by(TrainingRun.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_best_model_run(
        self, db: Session, *, user_id: int
    ) -> Optional[TrainingRun]:
        """Get the best model training run for a user."""
        return (
            db.query(TrainingRun)
            .filter(TrainingRun.user_id == user_id, TrainingRun.is_best_model == True)
            .order_by(TrainingRun.created_at.desc())
            .first()
        )

    def get_latest(self, db: Session) -> Optional[TrainingRun]:
        """Get the most recent training run."""
        return (
            db.query(TrainingRun)
            .order_by(TrainingRun.created_at.desc())
            .first()
        )


training_repository = TrainingRepository()
