import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class SubtaskBase(BaseModel):
    title: str
    is_completed: bool = False
    position: int

class SubtaskCreateRequest(BaseModel):
    title: str

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Judul subtask tidak boleh kosong")
        return v.strip()

class SubtaskCreate(SubtaskBase):
    task_id: uuid.UUID

class SubtaskUpdateRequest(BaseModel):
    title: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Judul subtask tidak boleh kosong")
            return v.strip()
        return v

class SubtaskUpdateResponse(BaseModel):
    id: uuid.UUID
    title: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubtaskCompleteRequest(BaseModel):
    is_completed: bool

    @field_validator('is_completed', mode='before')
    @classmethod
    def validate_is_completed(cls, v):
        if isinstance(v, bool):
            return v
        if str(v).lower() not in ['true', 'false', '1', '0']:
            raise ValueError("Format status penyelesaian tidak valid. Harap gunakan tipe boolean (true/false)")
        return v

class SubtaskCompleteResponse(BaseModel):
    id: uuid.UUID
    is_completed: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubtaskMoveRequest(BaseModel):
    position: int

    @field_validator('position')
    @classmethod
    def validate_position(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Posisi subtask minimal adalah 1")
        return v

class SubtaskResponse(SubtaskBase):
    id: uuid.UUID
    task_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SubtaskSimpleResponse(BaseModel):
    id: uuid.UUID
    title: str
    is_completed: bool
    position: int

    model_config = ConfigDict(from_attributes=True)

class SubtaskMoveResponse(BaseModel):
    id: uuid.UUID
    position: int

    model_config = ConfigDict(from_attributes=True)