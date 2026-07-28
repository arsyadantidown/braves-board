import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update, func
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


    async def get_member_include_deleted(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> BoardMember | None:

        stmt = (
            select(BoardMember)
            .where(
                BoardMember.board_id == board_id,
                BoardMember.user_id == user_id,
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


    async def count_owners(
        self,
        board_id: uuid.UUID,
    ) -> int:

        stmt = (
            select(func.count())
            .select_from(BoardMember)
            .where(
                BoardMember.board_id == board_id,
                BoardMember.role == BoardRole.OWNER,
                BoardMember.deleted_at.is_(None),
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one()


    async def create(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
        role: BoardRole = BoardRole.MEMBER,
    ) -> BoardMember:


        existing = await self.get_member_include_deleted(
            board_id,
            user_id,
        )


        if existing:

            existing.role = role
            existing.deleted_at = None
            existing.updated_at = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(existing)

            return existing


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

        member = await self.get_member(
            board_id,
            user_id,
        )

        if not member:
            return False

        # jangan sampai owner terakhir hilang
        if member.role == BoardRole.OWNER:
            owner_count = await self.count_owners(board_id)

            if owner_count <= 1:
                return False

        member.deleted_at = datetime.now(timezone.utc)

        await self.session.commit()

        return True