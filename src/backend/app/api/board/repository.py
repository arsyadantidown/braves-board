import uuid
from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board_model import Board
from app.api.board.schema import BoardCreate
from app.models.board_member_model import BoardMember

class BoardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Board | None:
        stmt = (
            select(Board)
            .options(
                selectinload(Board.columns)
            )
            .join(
                BoardMember,
                BoardMember.board_id == Board.id,
            )
            .where(
                Board.id == board_id,
                BoardMember.user_id == user_id,
                BoardMember.deleted_at.is_(None),
                Board.deleted_at.is_(None),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> Sequence[Board]:
        stmt = (
            select(Board)
            .join(
                BoardMember,
                BoardMember.board_id == Board.id,
            )
            .where(
                BoardMember.user_id == user_id,
                BoardMember.deleted_at.is_(None),
                Board.deleted_at.is_(None),
            )
            .order_by(Board.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, board_in: BoardCreate, user_id: uuid.UUID) -> Board:
        db_board = Board(**board_in.model_dump(), user_id=user_id)
        self.session.add(db_board)
        await self.session.commit()
        await self.session.refresh(db_board)
        return db_board

    async def update(self, board_id: uuid.UUID, update_data: dict, user_id: uuid.UUID) -> Board | None:
        allowed_fields = {"title"}

        filtered_data = {
            key: value for key, value in update_data.items()
            if key in allowed_fields
        }

        if not filtered_data:
            return None

        stmt = (
            update(Board)
            .where(
                Board.id == board_id,
                Board.user_id == user_id,
                Board.deleted_at.is_(None)
            )
            .values(**filtered_data, updated_at=datetime.now(timezone.utc))
            .returning(Board)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def soft_delete(self, board_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = (
            update(Board)
            .where(
                Board.id == board_id,
                Board.user_id == user_id,
                Board.deleted_at.is_(None)
            )
            .values(deleted_at=datetime.now(timezone.utc))
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0