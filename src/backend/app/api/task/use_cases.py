import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.task.repository import TaskRepository
from app.api.column.repository import ColumnRepository
from app.api.user.repository import UserRepository

from app.api.notification.repository import NotificationRepository
from app.api.notification.use_cases import NotificationUseCase

from app.api.task_activity.use_cases import ActivityUseCase
from app.models.user_model import User

from app.api.task.schema import (
    TaskCreateRequest,
    TaskCreate,
    TaskDetailResponse,
    TaskUpdateRequest,
    TaskCompleteRequest,
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

        self.activity_use_case = ActivityUseCase(session)

    async def create_task(
        self,
        request: TaskCreateRequest,
        current_user: User,
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

        await self.activity_use_case.create(
            board_id=column.board_id,
            user_id=current_user.id,
            task_id=task.id,
            action="task_created",
            description=(
                f'{current_user.full_name} created task '
                f'"{task.title}"'
            ),
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
        archived: bool = False,
        assignee_id: uuid.UUID | None = None,
    ):
        column = await self.column_repo.get_by_id(
            column_id
        )

        if not column:
            raise ColumnNotFoundException()

        records = await self.task_repo.get_all_by_column_id_with_counts(
            column_id,
            archived,
            assignee_id,
        )

        return [
            {
                "id": task.id,
                "title": task.title,
                "position": task.position,
                "due_date": task.due_date,
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
        current_user: User,
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        # Snapshot old values before update
        old_title = task.title
        old_description = task.description
        old_due_date = task.due_date
        old_assignee_ids = set(task.assignee_ids or [])

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

        if not updated_task:
            raise TaskNotFoundException()

        column = await self.column_repo.get_by_id(
            updated_task.column_id
        )

        if not column:
            raise ColumnNotFoundException()

        if (
            "title" in update_data
            and update_data["title"] != old_title
        ):
            await self.activity_use_case.create(
                board_id=column.board_id,
                user_id=current_user.id,
                task_id=updated_task.id,
                action="task_updated",
                description=(
                    f'{current_user.full_name} changed task title '
                    f'from "{old_title}" to "{updated_task.title}"'
                ),
                details={
                    "old_title": old_title,
                    "new_title": updated_task.title,
                },
            )

        if (
            "description" in update_data
            and update_data["description"] != old_description
        ):
            await self.activity_use_case.create(
                board_id=column.board_id,
                user_id=current_user.id,
                task_id=updated_task.id,
                action="task_updated",
                description=(
                    f'{current_user.full_name} changed task description'
                ),
                details={
                    "old_description": old_description,
                    "new_description": updated_task.description,
                },
            )

        if (
            "due_date" in update_data
            and update_data["due_date"] != old_due_date
        ):
            new_due_date = updated_task.due_date

            if old_due_date is None and new_due_date is not None:
                action = "due_date_set"
                description = (
                    f'{current_user.full_name} set due date for '
                    f'task "{updated_task.title}"'
                )

            elif old_due_date is not None and new_due_date is None:
                action = "due_date_removed"
                description = (
                    f'{current_user.full_name} removed due date from '
                    f'task "{updated_task.title}"'
                )

            else:
                action = "due_date_changed"
                description = (
                    f'{current_user.full_name} changed due date for '
                    f'task "{updated_task.title}"'
                )

            await self.activity_use_case.create(
                board_id=column.board_id,
                user_id=current_user.id,
                task_id=updated_task.id,
                action=action,
                description=description,
                details={
                    "old_due_date": (
                        old_due_date.isoformat()
                        if old_due_date
                        else None
                    ),
                    "new_due_date": (
                        new_due_date.isoformat()
                        if new_due_date
                        else None
                    ),
                },
            )

        if "assignee_ids" in update_data:
            new_assignee_ids = set(
                updated_task.assignee_ids or []
            )

            added_assignees = new_assignee_ids - old_assignee_ids
            removed_assignees = old_assignee_ids - new_assignee_ids

            for user_id in added_assignees:
                await self.activity_use_case.create(
                    board_id=column.board_id,
                    user_id=current_user.id,
                    task_id=updated_task.id,
                    action="task_assigned",
                    description=(
                        f'{current_user.full_name} assigned a member '
                        f'to task "{updated_task.title}"'
                    ),
                    details={
                        "assignee_id": str(user_id),
                    },
                )

            for user_id in removed_assignees:
                await self.activity_use_case.create(
                    board_id=column.board_id,
                    user_id=current_user.id,
                    task_id=updated_task.id,
                    action="task_unassigned",
                    description=(
                        f'{current_user.full_name} unassigned a member '
                        f'from task "{updated_task.title}"'
                    ),
                    details={
                        "assignee_id": str(user_id),
                    },
                )

        for user_id in updated_task.assignee_ids or []:
            await self.notification_use_case.create(
                user_id=user_id,
                board_id=column.board_id,
                task_id=updated_task.id,
                type="task_updated",
                title="Task Updated",
                message=(
                    f'Task "{updated_task.title}" has been updated.'
                ),
            )

        return {
            "id": updated_task.id,
            "updated_at": updated_task.updated_at,
        }

    async def complete_task(
        self,
        task_id: uuid.UUID,
        request: TaskCompleteRequest,
        current_user: User,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        updated_task = await self.task_repo.update(
            task_id,
            {
                "is_completed": request.is_completed,
            },
        )

        if not updated_task:
            raise TaskNotFoundException()

        column = await self.column_repo.get_by_id(
            updated_task.column_id
        )

        if not column:
            raise ColumnNotFoundException()

        action = (
            "task_completed"
            if updated_task.is_completed
            else "task_uncompleted"
        )

        description = (
            f'{current_user.full_name} '
            f'{"completed" if updated_task.is_completed else "uncompleted"} '
            f'task "{updated_task.title}"'
        )

        await self.activity_use_case.create(
            board_id=column.board_id,
            user_id=current_user.id,
            task_id=updated_task.id,
            action=action,
            description=description,
        )

        return {
            "id": updated_task.id,
            "is_completed": updated_task.is_completed,
            "updated_at": updated_task.updated_at,
        }

    async def archive_task(
        self,
        task_id: uuid.UUID,
        current_user: User,
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

        column = await self.column_repo.get_by_id(
            archived_task.column_id
        )

        if not column:
            raise ColumnNotFoundException()

        await self.activity_use_case.create(
            board_id=column.board_id,
            user_id=current_user.id,
            task_id=archived_task.id,
            action="task_archived",
            description=(
                f'{current_user.full_name} archived task '
                f'"{archived_task.title}"'
            ),
        )

        return {
            "id": archived_task.id,
            "is_archived": archived_task.is_archived,
            "updated_at": archived_task.updated_at,
        }

    async def unarchive_task(
        self,
        task_id: uuid.UUID,
        current_user: User,
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

        column = await self.column_repo.get_by_id(
            unarchived_task.column_id
        )

        if not column:
            raise ColumnNotFoundException()

        await self.activity_use_case.create(
            board_id=column.board_id,
            user_id=current_user.id,
            task_id=unarchived_task.id,
            action="task_unarchived",
            description=(
                f'{current_user.full_name} unarchived task '
                f'"{unarchived_task.title}"'
            ),
        )

        return {
            "id": unarchived_task.id,
            "is_archived": unarchived_task.is_archived,
            "updated_at": unarchived_task.updated_at,
        }

    async def move_task(
        self,
        task_id: uuid.UUID,
        request: TaskMoveRequest,
        current_user: User,
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

        old_column = await self.column_repo.get_by_id(
            old_column_id
        )

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

        if not same_column:
            await self.activity_use_case.create(
                board_id=target_column.board_id,
                user_id=current_user.id,
                task_id=updated_task.id,
                action="task_moved",
                description=(
                    f'{current_user.full_name} moved task '
                    f'"{updated_task.title}" from '
                    f'"{old_column.title}" to '
                    f'"{target_column.title}"'
                ),
                details={
                    "from_column_id": str(old_column.id),
                    "from_column_name": old_column.title,
                    "to_column_id": str(target_column.id),
                    "to_column_name": target_column.title,
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
        current_user: User,
    ):
        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        column = await self.column_repo.get_by_id(
            task.column_id
        )

        if not column:
            raise ColumnNotFoundException()

        deleted = await self.task_repo.soft_delete(
            task_id
        )

        if not deleted:
            raise TaskNotFoundException()

        await self.task_repo.cascade_soft_delete_subtasks(
            task_id
        )

        await self.activity_use_case.create(
            board_id=column.board_id,
            user_id=current_user.id,
            task_id=task.id,
            action="task_deleted",
            description=(
                f'{current_user.full_name} deleted task '
                f'"{task.title}"'
            ),
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