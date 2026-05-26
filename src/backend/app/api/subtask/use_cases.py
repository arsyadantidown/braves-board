import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.subtask.repository import SubtaskRepository
from app.api.task.repository import TaskRepository
from app.api.subtask.schema import (
    SubtaskCreateRequest,
    SubtaskCreate,
    SubtaskSimpleResponse,
    SubtaskUpdateRequest,
    SubtaskUpdateResponse,
    SubtaskCompleteRequest,
    SubtaskCompleteResponse,
    SubtaskMoveRequest,
    SubtaskMoveResponse,
)
from app.api.exceptions.task_exceptions import TaskNotFoundException
from app.api.exceptions.subtask_exceptions import (
    SubtaskNotFoundException,
    NoSubtaskFieldsToUpdateException,
    InvalidSubtaskPositionException,
    InvalidSubtaskStatusException,
)

class SubtaskUseCase:
    def __init__(self, db: AsyncSession):
        self.subtask_repo = SubtaskRepository(db)
        self.task_repo = TaskRepository(db)

    async def create_subtask(self, task_id: uuid.UUID, payload: SubtaskCreateRequest):
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException()

        max_position = await self.subtask_repo.get_max_position(task_id)
        next_position = max_position + 1

        subtask_in = SubtaskCreate(
            task_id=task_id,
            title=payload.title,
            position=next_position
        )
        subtask = await self.subtask_repo.create(subtask_in)

        return SubtaskSimpleResponse.model_validate(subtask).model_dump()

    async def update_subtask(self, subtask_id: uuid.UUID, payload: SubtaskUpdateRequest):
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise NoSubtaskFieldsToUpdateException()

        subtask = await self.subtask_repo.get_by_id(subtask_id)
        if not subtask:
            raise SubtaskNotFoundException()

        updated_subtask = await self.subtask_repo.update(subtask_id, update_data)

        return SubtaskUpdateResponse.model_validate(updated_subtask).model_dump()

    async def complete_subtask(self, subtask_id: uuid.UUID, payload: SubtaskCompleteRequest):
        if not isinstance(payload.is_completed, bool):
            raise InvalidSubtaskStatusException()

        subtask = await self.subtask_repo.get_by_id(subtask_id)
        if not subtask:
            raise SubtaskNotFoundException()

        updated_subtask = await self.subtask_repo.update(
            subtask_id, {"is_completed": payload.is_completed}
        )

        return SubtaskCompleteResponse.model_validate(updated_subtask).model_dump()

    async def move_subtask(self, subtask_id: uuid.UUID, payload: SubtaskMoveRequest):
        subtask = await self.subtask_repo.get_by_id(subtask_id)
        if not subtask:
            raise SubtaskNotFoundException()

        max_position = await self.subtask_repo.get_max_position(subtask.task_id)
        new_position = payload.position
        old_position = subtask.position

        if new_position > max_position:
            new_position = max_position

        if new_position == old_position:
            return SubtaskMoveResponse.model_validate(subtask).model_dump()

        if new_position < old_position:
            await self.subtask_repo.shift_positions(
                task_id=subtask.task_id,
                from_position=new_position,
                to_position=old_position - 1,
                shift=+1
            )
        else:
            await self.subtask_repo.shift_positions(
                task_id=subtask.task_id,
                from_position=old_position + 1,
                to_position=new_position,
                shift=-1
            )

        updated_subtask = await self.subtask_repo.update(
            subtask_id, {"position": new_position}
        )

        return SubtaskMoveResponse.model_validate(updated_subtask).model_dump()

    async def delete_subtask(self, subtask_id: uuid.UUID) -> None:
        subtask = await self.subtask_repo.get_by_id(subtask_id)
        if not subtask:
            raise SubtaskNotFoundException()

        deleted_position = subtask.position
        task_id = subtask.task_id

        await self.subtask_repo.soft_delete(subtask_id)

        max_position = await self.subtask_repo.get_max_position(task_id)
        if deleted_position <= max_position:
            await self.subtask_repo.shift_positions(
                task_id=task_id,
                from_position=deleted_position + 1,
                to_position=max_position + 1,
                shift=-1
            )