import uuid
from typing import Sequence

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_log_model import TimeLog
from app.api.time_tracking.schema import TimeLogCreate


class TimeLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        log_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> TimeLog | None:
        stmt = select(TimeLog).where(
            TimeLog.id == log_id
        )

        if user_id is not None:
            stmt = stmt.where(
                TimeLog.user_id == user_id
            )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_task_id(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Sequence[TimeLog]:
        stmt = (
            select(TimeLog)
            .where(
                TimeLog.task_id == task_id
            )
        )

        if user_id is not None:
            stmt = stmt.where(
                TimeLog.user_id == user_id
            )

        stmt = stmt.order_by(TimeLog.created_at)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        log_in: TimeLogCreate,
        user_id: uuid.UUID,
    ) -> TimeLog:
        db_log = TimeLog(
            **log_in.model_dump(),
            user_id=user_id,
        )

        self.session.add(db_log)
        await self.session.commit()
        await self.session.refresh(db_log)

        return db_log

    async def update(
        self,
        log_id: uuid.UUID,
        update_data: dict,
        user_id: uuid.UUID | None = None,
    ) -> TimeLog | None:
        stmt = (
            update(TimeLog)
            .where(
                TimeLog.id == log_id
            )
        )

        if user_id is not None:
            stmt = stmt.where(
                TimeLog.user_id == user_id
            )

        stmt = (
            stmt
            .values(**update_data)
            .returning(TimeLog)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar_one_or_none()

    async def delete(
        self,
        log_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        stmt = (
            delete(TimeLog)
            .where(
                TimeLog.id == log_id,
                TimeLog.user_id == user_id,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0