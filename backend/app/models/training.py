from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    algorithm = Column(
        String(100),
        nullable=False
    )

    dataset_name = Column(
        String(255),
        nullable=False
    )

    dataset_size = Column(
        Integer,
        nullable=False
    )

    accuracy = Column(
        Float,
        nullable=False
    )

    precision = Column(
        Float,
        nullable=False
    )

    recall = Column(
        Float,
        nullable=False
    )

    f1_score = Column(
        Float,
        nullable=False
    )

    roc_auc = Column(
        Float,
        nullable=False
    )

    training_time = Column(
        Float,
        nullable=False
    )

    hyperparameters = Column(
        Text,
        nullable=True
    )

    model_path = Column(
        String(500),
        nullable=True
    )

    is_best_model = Column(
        Boolean,
        default=False
    )

    status = Column(
        String(50),
        default="Completed"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="training_runs"
    )