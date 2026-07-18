from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    project_name = Column(
        String(200),
        nullable=False
    )

    repository_url = Column(
        String(500),
        nullable=True
    )

    source_code_path = Column(
        String(500),
        nullable=True
    )

    language = Column(
        String(50),
        nullable=False,
        default="Python"
    )

    framework = Column(
        String(100),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    version = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(50),
        default="Uploaded"
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

    # ===========================
    # Relationships
    # ===========================

    owner = relationship(
        "User",
        back_populates="projects"
    )

    metrics = relationship(
        "ApiMetric",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    predictions = relationship(
        "Prediction",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    cicd_scans = relationship(
        "CICDScan",
        back_populates="project",
        cascade="all, delete-orphan"
    )