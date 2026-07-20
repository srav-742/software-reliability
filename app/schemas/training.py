"""
Pydantic schemas for ML training API requests and responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TrainingRequest(BaseModel):
    """Request schema for triggering model training."""
    algorithms: Optional[List[str]] = None  # None = train all models
    test_size: Optional[float] = 0.2
    dataset_path: Optional[str] = None  # None = use synthetic dataset


class ModelMetrics(BaseModel):
    """Metrics for a single trained model."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float


class ModelResult(BaseModel):
    """Result for a single model after training."""
    algorithm: str
    metrics: ModelMetrics
    training_time: float
    error: Optional[str] = None


class TrainingResponse(BaseModel):
    """Response schema for training endpoint."""
    status: str
    message: str
    dataset_size: int
    best_algorithm: str
    best_metrics: ModelMetrics
    all_results: List[ModelResult]
    model_paths: Dict[str, str]


class TrainingRunResponse(BaseModel):
    """Response schema mapped to the TrainingRun DB model."""
    id: int
    user_id: int
    algorithm: str
    dataset_name: str
    dataset_size: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    training_time: float
    hyperparameters: Optional[str] = None
    model_path: Optional[str] = None
    is_best_model: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
