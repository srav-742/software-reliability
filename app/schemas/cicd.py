from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class CICDScanResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    author: Optional[str] = None
    risk_score: float  # Percentage 0 to 100
    failure_probability: float  # 0.0 to 1.0
    status: str  # PASS, WARN, FAIL
    pass_threshold: float
    warn_threshold: float
    metrics_summary: Optional[Dict[str, Any]] = None
    report_markdown: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CICDScanSummaryResponse(BaseModel):
    id: int
    project_id: int
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    author: Optional[str] = None
    risk_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
