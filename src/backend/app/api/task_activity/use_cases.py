import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.task_activity.repository import ActivityRepository


class ActivityUseCase:
    def __init__(self, session: AsyncSession):
        self.activity_repo = ActivityRepository(session)

    async def create(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        description: str,
        task_id: uuid.UUID | None = None,
        details: dict | None = None,
    ):
        return await self.activity_repo.create(
            board_id=board_id,
            user_id=user_id,
            task_id=task_id,
            action=action,
            description=description,
            details=details,
        )

    async def get_by_board(
        self,
        board_id: uuid.UUID,
    ):
        return await self.activity_repo.get_all_by_board_id(
            board_id
        )

    async def get_by_task(
        self,
        task_id: uuid.UUID,
    ):
        return await self.activity_repo.get_all_by_task_id(
            task_id
        )