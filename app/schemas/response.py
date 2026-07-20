"""
Generic response schemas used across the Software Reliability API.
"""

from typing import Optional, Any, Dict, List
from pydantic import BaseModel


class StatusResponse(BaseModel):
    """Generic status response."""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class ModelRegistryResponse(BaseModel):
    """Response schema for model registry entries."""
    id: int
    model_name: str
    algorithm: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    framework: str
    description: Optional[str] = None
    is_active: bool
