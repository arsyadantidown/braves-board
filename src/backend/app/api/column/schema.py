import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class ColumnBase(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Title tidak boleh kosong")
        return v.strip()


class ColumnCreate(ColumnBase):
    board_id: uuid.UUID


class ColumnUpdate(BaseModel):
    title: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Title tidak boleh kosong")
        return v.strip()


class ColumnResponse(ColumnBase):
    id: uuid.UUID
    board_id: uuid.UUID
    position: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
