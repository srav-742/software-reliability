from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ApiMetric(Base):
    __tablename__ = "api_metrics"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    # -----------------------------
    # Source Code Metrics
    # -----------------------------

    lines_of_code = Column(Integer, nullable=False)

    cyclomatic_complexity = Column(Integer, nullable=False)

    number_of_functions = Column(Integer, nullable=False)

    number_of_parameters = Column(Integer, nullable=False)

    nested_depth = Column(Integer, nullable=False)

    if_statement_count = Column(Integer, nullable=False)

    loop_count = Column(Integer, nullable=False)

    imports_count = Column(Integer, nullable=False)

    dependency_count = Column(Integer, nullable=False)

    duplicate_code_score = Column(Float, nullable=False)

    exception_handling_count = Column(Integer, nullable=False)

    database_queries = Column(Integer, nullable=False)

    external_api_calls = Column(Integer, nullable=False)

    # -----------------------------
    # Runtime Metrics
    # -----------------------------

    cpu_usage = Column(Float, nullable=False)

    memory_usage = Column(Float, nullable=False)

    average_response_time = Column(Float, nullable=False)

    # -----------------------------
    # Quality Metrics
    # -----------------------------

    test_coverage = Column(Float, nullable=False)

    historical_bug_count = Column(Integer, nullable=False)

    # -----------------------------
    # Target Label
    # -----------------------------

    api_failure = Column(
        Integer,
        nullable=False
    )

    # -----------------------------
    # Timestamp
    # -----------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # -----------------------------
    # Relationships
    # -----------------------------

    project = relationship(
        "Project",
        back_populates="metrics"
    )

    predictions = relationship(
        "Prediction",
        back_populates="metric",
        cascade="all, delete-orphan"
    )