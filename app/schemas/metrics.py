from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MetricBase(BaseModel):
    lines_of_code: int
    cyclomatic_complexity: int
    number_of_functions: int
    number_of_parameters: int
    nested_depth: int
    if_statement_count: int
    loop_count: int
    imports_count: int
    dependency_count: int
    duplicate_code_score: float
    exception_handling_count: int
    database_queries: int
    external_api_calls: int
    cpu_usage: float
    memory_usage: float
    average_response_time: float
    test_coverage: float
    historical_bug_count: int
    api_failure: int


class MetricCreate(MetricBase):
    project_id: int


class MetricUpdate(BaseModel):
    lines_of_code: Optional[int] = None
    cyclomatic_complexity: Optional[int] = None
    number_of_functions: Optional[int] = None
    number_of_parameters: Optional[int] = None
    nested_depth: Optional[int] = None
    if_statement_count: Optional[int] = None
    loop_count: Optional[int] = None
    imports_count: Optional[int] = None
    dependency_count: Optional[int] = None
    duplicate_code_score: Optional[float] = None
    exception_handling_count: Optional[int] = None
    database_queries: Optional[int] = None
    external_api_calls: Optional[int] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    average_response_time: Optional[float] = None
    test_coverage: Optional[float] = None
    historical_bug_count: Optional[int] = None
    api_failure: Optional[int] = None


class MetricResponse(MetricBase):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
