import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class TaskCommentBase(BaseModel):
    content: str

class TaskCommentCreate(TaskCommentBase):
    task_id: uuid.UUID
    user_id: uuid.UUID

class TaskCommentResponse(TaskCommentBase):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AddCommentRequest(BaseModel):
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Isi komentar tidak boleh kosong")
        return v.strip()