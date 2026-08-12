import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.connections.postgres import Base

if TYPE_CHECKING:
    from app.models.subtask_model import Subtask
    from app.models.task_comment_model import TaskComment
    from app.models.task_attachment_model import TaskAttachment

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    column_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("columns.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    labels: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    is_timer_running: Mapped[bool] = mapped_column(Boolean, server_default="false", index=True, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, server_default="false", index=True, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, server_default="false", index=True, nullable=False)

    start_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_duration: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    assignee_ids: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)), index=True, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

    column = relationship("Column", back_populates="tasks")
    subtasks: Mapped[list["Subtask"]] = relationship(back_populates="task")
    comments: Mapped[list["TaskComment"]] = relationship(back_populates="task")
    attachments: Mapped[list["TaskAttachment"]] = relationship(back_populates="task")
    notifications = relationship("Notification", back_populates="task")