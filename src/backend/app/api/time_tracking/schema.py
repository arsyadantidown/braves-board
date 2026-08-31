import uuid
from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict


class TimerPayload(BaseModel):
    description: Optional[str] = None


class TimerStopPayload(BaseModel):
    reason: Literal[
        "manual",
        "normal_close",
        "no_response",
        "unexpected_close",
    ] = "manual"


class TimeLogCreate(BaseModel):
    task_id: uuid.UUID
    start_time: datetime
    activity_description: Optional[str] = None


class TimeLogUpdate(BaseModel):
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    activity_description: Optional[str] = None


class TimeLogItem(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    start_time: datetime
    stop_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    activity_description: Optional[str] = None
    stop_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeLogsResponse(BaseModel):
    task_id: uuid.UUID
    count: int
    logs: List[TimeLogItem]