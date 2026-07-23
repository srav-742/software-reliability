"""
Database models for API Key Scan results.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ApiKeyScan(Base):
    """Stores the summary result of an API key scan for a project."""
    __tablename__ = "api_key_scans"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    total_keys_found = Column(Integer, nullable=False, default=0)
    valid_keys = Column(Integer, nullable=False, default=0)
    invalid_keys = Column(Integer, nullable=False, default=0)
    unknown_keys = Column(Integer, nullable=False, default=0)

    scan_status = Column(
        String(50),
        nullable=False,
        default="in_progress",
    )

    scanned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    project = relationship("Project", back_populates="api_key_scans")
    detected_keys = relationship(
        "DetectedApiKey",
        back_populates="scan",
        cascade="all, delete-orphan",
    )


class DetectedApiKey(Base):
    """Individual API key detected within a scan."""
    __tablename__ = "detected_api_keys"

    id = Column(Integer, primary_key=True, index=True)

    scan_id = Column(
        Integer,
        ForeignKey("api_key_scans.id", ondelete="CASCADE"),
        nullable=False,
    )

    provider = Column(String(50), nullable=False)
    key_masked = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    line_number = Column(Integer, nullable=False, default=1)

    status = Column(
        String(30),
        nullable=False,
        default="unknown",
    )

    failure_chance = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(30), nullable=False, default="low")

    error_message = Column(Text, nullable=True)

    # Relationships
    scan = relationship("ApiKeyScan", back_populates="detected_keys")
