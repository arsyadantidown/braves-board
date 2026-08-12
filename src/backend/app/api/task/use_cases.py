import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.task.repository import TaskRepository
from app.api.column.repository import ColumnRepository
from app.api.user.repository import UserRepository

from app.api.notification.repository import NotificationRepository
from app.api.notification.use_cases import NotificationUseCase

from app.api.task.schema import (
    TaskCreateRequest,
    TaskCreate,
    TaskDetailResponse,
    TaskUpdateRequest,
    TaskMoveRequest,
    TaskMoveResponse,
    TaskReorderRequest,
    TaskReorderResponse,
)

from app.api.exceptions.task_exceptions import (
    ColumnNotFoundException,
    TaskNotFoundException,
    InvalidTargetColumnException,
    InvalidAssigneeException,
)


class TaskUseCase:
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.column_repo = ColumnRepository(session)
        self.user_repo = UserRepository(session)

        self.notification_use_case = NotificationUseCase(
            NotificationRepository(session)
        )

    async def create_task(
        self,
        request: TaskCreateRequest,
    ):
        column = await self.column_repo.get_by_id(
            request.column_id
        )

        if not column:
            raise ColumnNotFoundException()

        if request.assignee_ids:
            users_valid = await self.user_repo.check_users_exist(
                request.assignee_ids
            )

            if not users_valid:
                raise InvalidAssigneeException()

        existing_tasks = await self.task_repo.get_all_by_column_id(
            request.column_id
        )

        task_data = TaskCreate(
            **request.model_dump(),
            position=len(existing_tasks) + 1,
        )

        task = await self.task_repo.create(
            task_data
        )

        for user_id in task.assignee_ids or []:
            await self.notification_use_case.create(
                user_id=user_id,
                board_id=column.board_id,
                task_id=task.id,
                type="task_created",
                title="Task Created",
                message=f'Task "{task.title}" has been created.',
            )

        return {
            "id": task.id,
            "title": task.title,
        }

    async def get_tasks_by_column(
        self,
        column_id: uuid.UUID,
    ):
        column = await self.column_repo.get_by_id(
            column_id
        )

        if not column:
            raise ColumnNotFoundException()

        records = await self.task_repo.get_all_by_column_id_with_counts(
            column_id
        )

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
                "is_timer_running": task.is_timer_running,
                "is_completed": task.is_completed,
                "is_archived": task.is_archived,
                "total_duration": task.total_duration,
            }
            for task, comment_count, attachment_count in records
        ]

    async def get_task_detail(
        self,
        task_id: uuid.UUID,
    ):
        task = await self.task_repo.get_detail_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        return TaskDetailResponse.model_validate(
            task
        ).model_dump(mode="json")

    async def update_task(
        self,
        task_id: uuid.UUID,
        request: TaskUpdateRequest,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        if request.assignee_ids is not None:
            users_valid = await self.user_repo.check_users_exist(
                request.assignee_ids
            )

            if not users_valid:
                raise InvalidAssigneeException()

        update_data = request.model_dump(
            exclude_unset=True
        )

        updated_task = await self.task_repo.update(
            task_id,
            update_data,
        )

        column = await self.column_repo.get_by_id(
            updated_task.column_id
        )

        for user_id in updated_task.assignee_ids or []:
            await self.notification_use_case.create(
                user_id=user_id,
                board_id=column.board_id,
                task_id=updated_task.id,
                type="task_updated",
                title="Task Updated",
                message=f'Task "{updated_task.title}" has been updated.',
            )

        return {
            "id": updated_task.id,
            "updated_at": updated_task.updated_at,
        }

    async def archive_task(
        self,
        task_id: uuid.UUID,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        archived_task = await self.task_repo.archive(
            task_id
        )

        if not archived_task:
            raise TaskNotFoundException()

        return {
            "id": archived_task.id,
            "is_archived": archived_task.is_archived,
            "updated_at": archived_task.updated_at,
        }

    async def unarchive_task(
        self,
        task_id: uuid.UUID,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        unarchived_task = await self.task_repo.unarchive(
            task_id
        )

        if not unarchived_task:
            raise TaskNotFoundException()

        return {
            "id": unarchived_task.id,
            "is_archived": unarchived_task.is_archived,
            "updated_at": unarchived_task.updated_at,
        }

    async def move_task(
        self,
        task_id: uuid.UUID,
        request: TaskMoveRequest,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        target_column = await self.column_repo.get_by_id(
            request.column_id
        )

        if not target_column:
            raise InvalidTargetColumnException()

        old_column_id = task.column_id
        old_position = task.position

        new_position = request.position

        target_max = await self.task_repo.get_max_position(
            request.column_id
        )

        same_column = (
            old_column_id == request.column_id
        )

        if same_column:

            if new_position > target_max:
                new_position = target_max

            if new_position == old_position:
                return TaskMoveResponse.model_validate(task)

        else:

            if new_position > target_max + 1:
                new_position = target_max + 1

        if same_column:

            if new_position < old_position:

                await self.task_repo.shift_positions(
                    column_id=old_column_id,
                    from_position=new_position,
                    to_position=old_position - 1,
                    shift=1,
                )

            else:

                await self.task_repo.shift_positions(
                    column_id=old_column_id,
                    from_position=old_position + 1,
                    to_position=new_position,
                    shift=-1,
                )

        else:

            source_max = await self.task_repo.get_max_position(
                old_column_id
            )

            if old_position < source_max:

                await self.task_repo.shift_positions(
                    column_id=old_column_id,
                    from_position=old_position + 1,
                    to_position=source_max,
                    shift=-1,
                )

            if new_position <= target_max:

                await self.task_repo.shift_positions(
                    column_id=request.column_id,
                    from_position=new_position,
                    to_position=target_max,
                    shift=1,
                )

        updated_task = await self.task_repo.update(
            task_id,
            {
                "column_id": request.column_id,
                "position": new_position,
            },
        )

        for user_id in updated_task.assignee_ids or []:

            await self.notification_use_case.create(
                user_id=user_id,
                board_id=target_column.board_id,
                task_id=updated_task.id,
                type="task_moved",
                title="Task Moved",
                message=f'Task "{updated_task.title}" has been moved.',
            )

        return TaskMoveResponse.model_validate(
            updated_task
        )

    async def reorder_task(
        self,
        task_id: uuid.UUID,
        request: TaskReorderRequest,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        max_position = await self.task_repo.get_max_position(
            task.column_id
        )

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
                shift=1,
            )

        else:

            await self.task_repo.shift_positions(
                column_id=task.column_id,
                from_position=old_position + 1,
                to_position=new_position,
                shift=-1,
            )

        updated_task = await self.task_repo.update(
            task_id,
            {
                "position": new_position,
            },
        )

        return TaskReorderResponse.model_validate(
            updated_task
        )

    async def delete_task(
        self,
        task_id: uuid.UUID,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        column = await self.column_repo.get_by_id(
            task.column_id
        )

        deleted = await self.task_repo.soft_delete(
            task_id
        )

        if not deleted:
            raise TaskNotFoundException()

        await self.task_repo.cascade_soft_delete_subtasks(
            task_id
        )

        for user_id in task.assignee_ids or []:

            await self.notification_use_case.create(
                user_id=user_id,
                board_id=column.board_id,
                task_id=task.id,
                type="task_deleted",
                title="Task Deleted",
                message=f'Task "{task.title}" has been deleted.',
            )

        return None