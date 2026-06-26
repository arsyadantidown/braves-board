import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class LogEntryData(BaseModel):
    """Schema for a single log entry returned by the API."""
    id: int
    timestamp: datetime
    log_type: str
    level: str
    logger_name: str
    message: str
    user_id: Optional[uuid.UUID] = None
    request_id: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    extra: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class LogListData(BaseModel):
    """Paginated log list response."""
    logs: list[LogEntryData]
    total: int
    page: int
    page_size: int
    total_pages: int


class LevelCountData(BaseModel):
    """Count per log level."""
    level: str
    count: int


class TypeCountData(BaseModel):
    """Count per log type."""
    log_type: str
    count: int


class LogStatsData(BaseModel):
    """Log statistics response."""
    total_count: int
    level_counts: list[LevelCountData]
    type_counts: list[TypeCountData]
    error_rate: float
    start: datetime
    end: datetime


class LogQueryParams(BaseModel):
    """Query parameters for filtering logs."""
    log_type: Optional[str] = None
    level: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    request_id: Optional[str] = None
    action: Optional[str] = None
    path: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    page: int = 1
    page_size: int = 50

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        if v < 1:
            return 1
        if v > 200:
            return 200
        return v

    @field_validator("page")
    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            return 1
        return v
