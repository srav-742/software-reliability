"""
Pydantic schemas for prediction API requests and responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReliabilityStats(BaseModel):
    """Software reliability growth model statistics."""
    failure_intensity: float
    mtbf_hours: float
    reliability_probability: float
    reliability_score: float
    operational_hours: float


class PredictionResponse(BaseModel):
    """Response schema for the predict endpoint."""
    project_id: int
    predicted_label: int
    failure_probability: float
    risk_level: str
    confidence_score: float
    reliability_stats: ReliabilityStats
    model_used: str
    recommendations: List[str] = []


class ShapFeatureContribution(BaseModel):
    """SHAP value for a single feature."""
    feature: str
    shap_value: float
    direction: str  # 'increases risk' or 'decreases risk'


class ExplanationResponse(BaseModel):
    """Response schema for the explain endpoint."""
    project_id: int
    model_used: str
    top_risk_factors: List[ShapFeatureContribution]
    shap_values: Dict[str, float]
    feature_importance: Dict[str, float]
    recommendations: List[str]


class PredictionDBResponse(BaseModel):
    """Response schema mapped to the Prediction DB model."""
    id: int
    project_id: int
    metric_id: int
    model_name: str
    failure_probability: float
    predicted_label: int
    risk_level: str
    confidence_score: float
    shap_summary: Optional[str] = None
    recommendations: Optional[str] = None
    prediction_time: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
