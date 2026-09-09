import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ActivityCreate(BaseModel):
    board_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    action: str
    description: str
    details: Optional[dict[str, Any]] = None


class ActivityResponse(BaseModel):
    id: uuid.UUID
    board_id: uuid.UUID
    user_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    action: str
    description: str
    details: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)