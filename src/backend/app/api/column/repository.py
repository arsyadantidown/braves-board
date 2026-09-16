import uuid
from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.column_model import Column
from app.api.column.schema import ColumnCreate


class ColumnRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, column_id: uuid.UUID) -> Column | None:
        stmt = select(Column).where(
            Column.id == column_id,
            Column.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_board_id(self, board_id: uuid.UUID) -> Sequence[Column]:
        stmt = (
            select(Column)
            .where(
                Column.board_id == board_id,
                Column.deleted_at.is_(None)
            )
            .order_by(Column.position)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, column_in: ColumnCreate) -> Column:
        last_position_stmt = select(func.max(Column.position)).where(
            Column.board_id == column_in.board_id,
            Column.deleted_at.is_(None)
        )
        result = await self.session.execute(last_position_stmt)
        last_position = result.scalar() or 0

        db_column = Column(
            **column_in.model_dump(),
            position=last_position + 1
        )

        self.session.add(db_column)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self.session.refresh(db_column)
        return db_column

    async def update(self, column_id: uuid.UUID, update_data: dict) -> Column | None:
        allowed_fields = {"title"}
        filtered_data = {
            k: v for k, v in update_data.items()
            if k in allowed_fields
        }

        column = await self.get_by_id(column_id)
        if not column:
            return None

        if not filtered_data:
            return column

        stmt = (
            update(Column)
            .where(
                Column.id == column_id,
                Column.deleted_at.is_(None)
            )
            .values(**filtered_data)
            .returning(Column)
        )

        result = await self.session.execute(stmt)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return result.scalar_one_or_none()

    async def soft_delete(self, column_id: uuid.UUID) -> bool:
        column = await self.get_by_id(column_id)
        if not column:
            return False

        stmt = (
            select(Column)
            .where(
                Column.board_id == column.board_id,
                Column.deleted_at.is_(None),
                Column.id != column_id
            )
            .order_by(Column.position)
        )
        result = await self.session.execute(stmt)
        columns = result.scalars().all()

        await self.session.execute(
            update(Column)
            .where(
                Column.id == column_id,
                Column.deleted_at.is_(None)
            )
            .values(deleted_at=datetime.now(timezone.utc))
        )

        for col in columns:
            await self.session.execute(
                update(Column)
                .where(
                    Column.id == col.id,
                    Column.deleted_at.is_(None)
                )
                .values(position=-(col.position + 1000))
            )

        await self.session.flush()

        for i, col in enumerate(columns, start=1):
            await self.session.execute(
                update(Column)
                .where(
                    Column.id == col.id,
                    Column.deleted_at.is_(None)
                )
                .values(position=i + 1000)
            )

        await self.session.flush()

        for i, col in enumerate(columns, start=1):
            await self.session.execute(
                update(Column)
                .where(
                    Column.id == col.id,
                    Column.deleted_at.is_(None)
                )
                .values(position=i)
            )

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return True

    async def cascade_soft_delete_by_board(
        self,
        board_id: uuid.UUID
    ) -> None:
        stmt = (
            update(Column)
            .where(
                Column.board_id == board_id,
                Column.deleted_at.is_(None),
            )
            .values(deleted_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def reorder(self, column_id: uuid.UUID, new_position: int) -> Column | None:
        column = await self.get_by_id(column_id)
        if not column:
            return None

        stmt = (
            select(Column)
            .where(
                Column.board_id == column.board_id,
                Column.deleted_at.is_(None)
            )
            .order_by(Column.position)
        )
        result = await self.session.execute(stmt)
        columns = result.scalars().all()

        total = len(columns)
        if new_position < 1 or new_position > total:
            return None

        old_index = next((i for i, c in enumerate(columns) if c.id == column_id), None)
        if old_index is None:
            return None

        if old_index == new_position - 1:
            return column

        for col in columns:
            await self.session.execute(
                update(Column)
                .where(
                    Column.id == col.id,
                    Column.deleted_at.is_(None)
                )
                .values(position=-(col.position + 1000))
            )

        await self.session.flush()

        target = columns.pop(old_index)
        columns.insert(new_position - 1, target) 

        for i, col in enumerate(columns, start=1):
            await self.session.execute(
                update(Column)
                .where(
                    Column.id == col.id,
                    Column.deleted_at.is_(None)
                )
                .values(position=i + 1000)
            )

        await self.session.flush()

        for i, col in enumerate(columns, start=1):
            await self.session.execute(
                update(Column)
                .where(
                    Column.id == col.id,
                    Column.deleted_at.is_(None)
                )
                .values(position=i)
            )

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self.session.refresh(target)
        return target