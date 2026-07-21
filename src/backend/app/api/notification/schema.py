import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    board_id: uuid.UUID
    task_id: uuid.UUID | None

    type: str
    title: str
    message: str

    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)