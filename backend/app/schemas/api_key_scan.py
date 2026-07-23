"""
Pydantic schemas for API Key Scan endpoints.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DetectedKeyResponse(BaseModel):
    """Schema for a single detected API key."""
    id: int
    provider: str
    key_masked: str
    file_path: str
    line_number: int
    status: str
    error_message: Optional[str] = None
    failure_chance: float
    risk_level: str

    class Config:
        from_attributes = True


class ApiKeyScanResponse(BaseModel):
    """Schema for a scan result summary."""
    id: int
    project_id: int
    total_keys_found: int
    valid_keys: int
    invalid_keys: int
    unknown_keys: int
    scan_status: str
    scanned_at: Optional[datetime] = None
    detected_keys: List[DetectedKeyResponse] = []

    class Config:
        from_attributes = True


class ApiKeyScanSummaryResponse(BaseModel):
    """Lightweight scan summary without detected keys (for history lists)."""
    id: int
    project_id: int
    total_keys_found: int
    valid_keys: int
    invalid_keys: int
    unknown_keys: int
    scan_status: str
    scanned_at: Optional[datetime] = None

    class Config:
        from_attributes = True
