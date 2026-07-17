import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.board_member_model import BoardRole


class BoardMemberBase(BaseModel):
    role: BoardRole = BoardRole.MEMBER


class BoardMemberCreate(BoardMemberBase):
    user_id: uuid.UUID


class BoardMemberUpdate(BaseModel):
    role: BoardRole


class BoardMemberResponse(BoardMemberBase):
    id: uuid.UUID
    board_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)