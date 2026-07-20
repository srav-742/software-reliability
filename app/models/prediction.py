from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    metric_id = Column(
        Integer,
        ForeignKey("api_metrics.id", ondelete="CASCADE"),
        nullable=False
    )

    model_name = Column(
        String(100),
        nullable=False
    )

    failure_probability = Column(
        Float,
        nullable=False
    )

    predicted_label = Column(
        Integer,
        nullable=False
    )

    risk_level = Column(
        String(20),
        nullable=False
    )

    confidence_score = Column(
        Float,
        nullable=False
    )

    shap_summary = Column(
        Text,
        nullable=True
    )

    recommendations = Column(
        Text,
        nullable=True
    )

    prediction_time = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ----------------------------------
    # Relationships
    # ----------------------------------

    project = relationship(
        "Project",
        back_populates="predictions"
    )

    metric = relationship(
        "ApiMetric",
        back_populates="predictions"
    )