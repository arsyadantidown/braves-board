import enum
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.connections.postgres import Base


class BoardRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class BoardMember(Base):
    __tablename__ = "board_members"

    __table_args__ = (
        Index(
            "uq_board_member_active",
            "board_id",
            "user_id",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boards.id"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    role: Mapped[BoardRole] = mapped_column(
        Enum(
            BoardRole,
            name="board_role",
        ),
        nullable=False,
        default=BoardRole.MEMBER,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=True,
    )

    board = relationship(
        "Board",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="board_members",
    )