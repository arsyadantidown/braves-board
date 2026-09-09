import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_model import Activity


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
        task_id: uuid.UUID | None,
        action: str,
        description: str,
        details: dict | None = None,
    ) -> Activity:
        activity = Activity(
            board_id=board_id,
            user_id=user_id,
            task_id=task_id,
            action=action,
            description=description,
            details=details,
        )

        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)

        return activity

    async def get_all_by_board_id(
        self,
        board_id: uuid.UUID,
    ) -> Sequence[Activity]:
        stmt = (
            select(Activity)
            .where(
                Activity.board_id == board_id,
            )
            .order_by(Activity.created_at.desc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def get_all_by_task_id(
        self,
        task_id: uuid.UUID,
    ) -> Sequence[Activity]:
        stmt = (
            select(Activity)
            .where(
                Activity.task_id == task_id,
            )
            .order_by(Activity.created_at.desc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()