from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.metrics import ApiMetric
from app.schemas.metrics import MetricCreate, MetricUpdate


class MetricsRepository:
    def create(self, db: Session, *, obj_in: MetricCreate) -> ApiMetric:
        db_obj = ApiMetric(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_project(self, db: Session, *, project_id: int) -> Optional[ApiMetric]:
        return (
            db.query(ApiMetric)
            .filter(ApiMetric.project_id == project_id)
            .order_by(ApiMetric.created_at.desc())
            .first()
        )

    def get_all_by_project(self, db: Session, *, project_id: int) -> List[ApiMetric]:
        return (
            db.query(ApiMetric)
            .filter(ApiMetric.project_id == project_id)
            .order_by(ApiMetric.created_at.desc())
            .all()
        )

    def update(
        self, db: Session, *, db_obj: ApiMetric, obj_in: MetricUpdate
    ) -> ApiMetric:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj


metrics_repository = MetricsRepository()
