from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    name: str = "GitHub Actions Key"


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApiKeyCreatedResponse(ApiKeyResponse):
    raw_key: str  # Only returned once upon creation
