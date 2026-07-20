from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200)
    repository_url: Optional[str] = Field(None, max_length=500)
    language: str = Field("Python", max_length=50)
    framework: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    repository_url: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=50)
    framework: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    source_code_path: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
