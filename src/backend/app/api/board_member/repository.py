import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board_member_model import BoardMember, BoardRole


class BoardMemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_member(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> BoardMember | None:
        stmt = (
            select(BoardMember)
            .where(
                BoardMember.board_id == board_id,
                BoardMember.user_id == user_id,
                BoardMember.deleted_at.is_(None),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_role(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> BoardRole | None:

        stmt = (
            select(BoardMember.role)
            .where(
                BoardMember.board_id == board_id,
                BoardMember.user_id == user_id,
                BoardMember.deleted_at.is_(None),
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        board_id: uuid.UUID,
    ) -> Sequence[BoardMember]:
        stmt = (
            select(BoardMember)
            .where(
                BoardMember.board_id == board_id,
                BoardMember.deleted_at.is_(None),
            )
            .order_by(BoardMember.created_at.asc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
        role: BoardRole = BoardRole.MEMBER,
    ) -> BoardMember:
        db_member = BoardMember(
            board_id=board_id,
            user_id=user_id,
            role=role,
        )

        self.session.add(db_member)

        await self.session.commit()
        await self.session.refresh(db_member)

        return db_member

    async def update(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
        role: BoardRole,
    ) -> BoardMember | None:
        stmt = (
            update(BoardMember)
            .where(
                BoardMember.board_id == board_id,
                BoardMember.user_id == user_id,
                BoardMember.deleted_at.is_(None),
            )
            .values(
                role=role,
                updated_at=datetime.now(timezone.utc),
            )
            .returning(BoardMember)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none()

    async def soft_delete(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        stmt = (
            update(BoardMember)
            .where(
                BoardMember.board_id == board_id,
                BoardMember.user_id == user_id,
                BoardMember.deleted_at.is_(None),
            )
            .values(
                deleted_at=datetime.now(timezone.utc),
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0