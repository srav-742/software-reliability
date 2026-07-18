from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class CICDScan(Base):
    __tablename__ = "cicd_scans"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    commit_sha = Column(String(100), nullable=True)

    branch = Column(String(100), nullable=True)

    author = Column(String(100), nullable=True)

    risk_score = Column(Float, nullable=False)  # Percentage 0.0 to 100.0

    failure_probability = Column(Float, nullable=False)  # 0.0 to 1.0

    status = Column(String(20), nullable=False)  # PASS, WARN, FAIL

    pass_threshold = Column(Float, default=50.0)

    warn_threshold = Column(Float, default=80.0)

    metrics_summary = Column(JSON, nullable=True)

    report_markdown = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    project = relationship("Project", back_populates="cicd_scans")
    user = relationship("User")
