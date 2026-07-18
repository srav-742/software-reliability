from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    Text,
    DateTime
)
from sqlalchemy.sql import func

from app.database.base import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)

    model_name = Column(
        String(150),
        nullable=False,
        unique=True
    )

    algorithm = Column(
        String(100),
        nullable=False
    )

    version = Column(
        String(50),
        nullable=False
    )

    model_path = Column(
        String(500),
        nullable=False
    )

    scaler_path = Column(
        String(500),
        nullable=True
    )

    encoder_path = Column(
        String(500),
        nullable=True
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

    framework = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
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