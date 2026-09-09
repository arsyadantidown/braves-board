import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.connections.postgres import Base

if TYPE_CHECKING:
    from app.models.board_model import Board
    from app.models.task_model import Task
    from app.models.user_model import User


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,server_default=func.gen_random_uuid())
    board_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("boards.id"),index=True,nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),index=True,nullable=False)
    task_id: Mapped[uuid.UUID | None] = mapped_column( UUID(as_uuid=True),ForeignKey("tasks.id"),index=True, nullable=True)
    action: Mapped[str] = mapped_column( String,nullable=False)
    description: Mapped[str] = mapped_column(Text,nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    board = relationship("Board", back_populates="activities")
    user = relationship("User", back_populates="activities")
    task = relationship("Task", back_populates="activities")