import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.task.repository import TaskRepository
from app.api.column.repository import ColumnRepository
from app.api.user.repository import UserRepository
from app.api.task.schema import (
    TaskCreateRequest, TaskCreate, TaskDetailResponse,
    TaskUpdateRequest, TaskMoveRequest, TaskMoveResponse,
    TaskReorderRequest, TaskReorderResponse,
)
from app.api.exceptions.task_exceptions import (
    ColumnNotFoundException, TaskNotFoundException,
    InvalidTargetColumnException, InvalidTaskPositionException,
    InvalidAssigneeException
)


class TaskUseCase:
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.column_repo = ColumnRepository(session)
        self.user_repo = UserRepository(session)

    async def create_task(self, request: TaskCreateRequest):
        column = await self.column_repo.get_by_id(request.column_id)

        if not column:
            raise ColumnNotFoundException()

        if request.assignee_ids:
            users_valid = await self.user_repo.check_users_exist(request.assignee_ids)
            if not users_valid:
                raise InvalidAssigneeException()

        existing_tasks = await self.task_repo.get_all_by_column_id(request.column_id)
        new_position = len(existing_tasks) + 1

        task_data = TaskCreate(
            **request.model_dump(),
            position=new_position
        )

        task = await self.task_repo.create(task_data)
        
        return {
            "id": task.id,
            "title": task.title
        }

    async def get_tasks_by_column(self, column_id: uuid.UUID):
        column = await self.column_repo.get_by_id(column_id)

        if not column:
            raise ColumnNotFoundException()

        records = await self.task_repo.get_all_by_column_id_with_counts(column_id)

        return [
            {
                "id": task.id,
                "title": task.title,
                "position": task.position,
                "due_date": task.due_date,
                "labels": task.labels,
                "assignee_ids": task.assignee_ids,
                "comment_count": comment_count,
                "attachment_count": attachment_count,
                "is_timer_running": task.is_timer_running
            }
            for task, comment_count, attachment_count in records
        ]

    async def get_task_detail(self, task_id: uuid.UUID):
        task = await self.task_repo.get_detail_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        return TaskDetailResponse.model_validate(task).model_dump(mode='json')

    async def update_task(self, task_id: uuid.UUID, request: TaskUpdateRequest):
        if request.assignee_ids is not None and len(request.assignee_ids) > 0:
            users_valid = await self.user_repo.check_users_exist(request.assignee_ids)
            if not users_valid:
                raise InvalidAssigneeException()

        update_data = request.model_dump(exclude_unset=True)
        updated_task = await self.task_repo.update(task_id, update_data)

        if not updated_task:
            raise TaskNotFoundException()

        return {
            "id": updated_task.id,
            "updated_at": updated_task.updated_at
        }

    async def move_task(self, task_id: uuid.UUID, request: TaskMoveRequest):
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException()

        target_column = await self.column_repo.get_by_id(request.column_id)
        if not target_column:
            raise InvalidTargetColumnException()

        new_position = request.position
        source_column_id = task.column_id
        old_position = task.position

        target_max = await self.task_repo.get_max_position(request.column_id)
        is_same_column = source_column_id == request.column_id

        if is_same_column:
            if new_position > target_max:
                new_position = target_max
            if new_position == old_position:
                return TaskMoveResponse.model_validate(task)
        else:
            if new_position > target_max + 1:
                new_position = target_max + 1

        if is_same_column:
            if new_position < old_position:
                await self.task_repo.shift_positions(
                    column_id=source_column_id,
                    from_position=new_position,
                    to_position=old_position - 1,
                    shift=+1
                )
            else:
                await self.task_repo.shift_positions(
                    column_id=source_column_id,
                    from_position=old_position + 1,
                    to_position=new_position,
                    shift=-1
                )
        else:
            source_max = await self.task_repo.get_max_position(source_column_id)
            if old_position < source_max:
                await self.task_repo.shift_positions(
                    column_id=source_column_id,
                    from_position=old_position + 1,
                    to_position=source_max,
                    shift=-1
                )

            if new_position <= target_max:
                await self.task_repo.shift_positions(
                    column_id=request.column_id,
                    from_position=new_position,
                    to_position=target_max,
                    shift=+1
                )

        updated_task = await self.task_repo.update(task_id, {
            "column_id": request.column_id,
            "position": new_position
        })

        return TaskMoveResponse.model_validate(updated_task)

    async def reorder_task(self, task_id: uuid.UUID, request: TaskReorderRequest):
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException()

        max_position = await self.task_repo.get_max_position(task.column_id)
        new_position = request.position
        old_position = task.position

        if new_position > max_position:
            new_position = max_position

        if new_position == old_position:
            return TaskReorderResponse.model_validate(task)

        if new_position < old_position:
            await self.task_repo.shift_positions(
                column_id=task.column_id,
                from_position=new_position,
                to_position=old_position - 1,
                shift=+1
            )
        else:
            await self.task_repo.shift_positions(
                column_id=task.column_id,
                from_position=old_position + 1,
                to_position=new_position,
                shift=-1
            )

        updated_task = await self.task_repo.update(task_id, {"position": new_position})

        return TaskReorderResponse.model_validate(updated_task)

    async def delete_task(self, task_id: uuid.UUID):
        is_deleted = await self.task_repo.soft_delete(task_id)

        if not is_deleted:
            raise TaskNotFoundException()

        await self.task_repo.cascade_soft_delete_subtasks(task_id)

        return None