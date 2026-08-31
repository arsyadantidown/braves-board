import uuid
from datetime import datetime
from typing import Optional, List, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    field_validator,
)


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    labels: Optional[List[str]] = None
    position: int
    is_timer_running: bool = False
    is_completed: bool = False
    is_archived: bool = False
    assignee_ids: Optional[List[uuid.UUID]] = None


class TaskCreate(TaskBase):
    column_id: uuid.UUID


class TaskListResponse(BaseModel):
    id: uuid.UUID
    title: str
    position: int
    due_date: Optional[datetime] = None
    labels: Optional[List[str]] = None
    assignee_ids: Optional[List[uuid.UUID]] = None
    comment_count: int
    attachment_count: int
    is_timer_running: bool
    is_completed: bool
    is_archived: bool
    total_duration: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class TaskCreateRequest(BaseModel):
    column_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    labels: Optional[List[str]] = None
    assignee_ids: Optional[List[uuid.UUID]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Judul task tidak boleh kosong")
        return v.strip()

    @field_validator("column_id", mode="before")
    @classmethod
    def validate_column_id(cls, v):
        try:
            return uuid.UUID(str(v))
        except ValueError:
            raise ValueError("Format column_id tidak valid")

    @field_validator("assignee_ids", mode="before")
    @classmethod
    def validate_assignee_ids(cls, v):
        if v is None:
            return v

        if not isinstance(v, list):
            raise ValueError("Format assignee_ids harus berupa array/list")

        for item in v:
            try:
                uuid.UUID(str(item))
            except ValueError:
                raise ValueError("Format UUID pada assignee_ids tidak valid")

        return v

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v):
        if v is None:
            return v

        if isinstance(v, str):
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Format tanggal tidak valid")

        return v


class SubtaskNestedResponse(BaseModel):
    id: uuid.UUID
    title: str
    is_completed: bool
    position: int

    model_config = ConfigDict(from_attributes=True)


class CommentNestedResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def map_user_name(cls, data: Any) -> Any:
        if hasattr(data, "user") and data.user:
            setattr(data, "user_name", data.user.full_name)

        return data


class AttachmentNestedResponse(BaseModel):
    id: uuid.UUID
    type: str
    file_name: str
    file_url: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskBase):
    id: uuid.UUID
    subtasks: List[SubtaskNestedResponse] = []
    comments: List[CommentNestedResponse] = []
    attachments: List[AttachmentNestedResponse] = []

    model_config = ConfigDict(from_attributes=True)


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    labels: Optional[List[str]] = None
    assignee_ids: Optional[List[uuid.UUID]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Judul task tidak boleh kosong")

            return v.strip()

        return v

    @field_validator("assignee_ids", mode="before")
    @classmethod
    def validate_assignee_ids(cls, v):
        if v is None:
            return v

        if not isinstance(v, list):
            raise ValueError("Format assignee_ids harus berupa array/list")

        for item in v:
            try:
                uuid.UUID(str(item))
            except ValueError:
                raise ValueError("Format UUID pada assignee_ids tidak valid")

        return v

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v):
        if v is None:
            return v

        if isinstance(v, str):
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Format tanggal tidak valid")

        return v


class TaskCompleteRequest(BaseModel):
    is_completed: bool


class TaskMoveRequest(BaseModel):
    column_id: uuid.UUID
    position: int

    @field_validator("column_id", mode="before")
    @classmethod
    def validate_column_id(cls, v):
        try:
            return uuid.UUID(str(v))
        except ValueError:
            raise ValueError("Format column_id tidak valid")

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Posisi task minimal adalah 1")

        return v


class TaskMoveResponse(BaseModel):
    id: uuid.UUID
    column_id: uuid.UUID
    position: int

    model_config = ConfigDict(from_attributes=True)


class TaskReorderRequest(BaseModel):
    position: int

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Posisi task minimal adalah 1")

        return v


class TaskReorderResponse(BaseModel):
    id: uuid.UUID
    position: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)