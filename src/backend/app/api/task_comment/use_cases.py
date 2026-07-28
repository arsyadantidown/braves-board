import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.task.repository import TaskRepository
from app.api.task_comment.repository import TaskCommentRepository
from app.api.task_comment.schema import TaskCommentCreate

from app.api.notification.repository import NotificationRepository
from app.api.notification.use_cases import NotificationUseCase

from app.api.exceptions.task_exceptions import TaskNotFoundException
from app.api.exceptions.task_comment_exceptions import (
    CommentNotFoundException,
    CommentForbiddenException,
)


class TaskCommentUseCase:
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.comment_repo = TaskCommentRepository(session)

        self.notification_use_case = NotificationUseCase(
            NotificationRepository(session)
        )


    async def add_comment(
        self,
        task_id: uuid.UUID,
        content: str,
        current_user_id: uuid.UUID,
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()


        comment_in = TaskCommentCreate(
            task_id=task_id,
            user_id=current_user_id,
            content=content,
        )


        comment = await self.comment_repo.create(
            comment_in
        )


        # notif ke assignee task kecuali pembuat comment
        for user_id in task.assignee_ids or []:

            if user_id == current_user_id:
                continue


            await self.notification_use_case.create(
                user_id=user_id,
                board_id=task.column.board_id,
                task_id=task.id,
                type="comment_created",
                title="New Comment",
                message=f'New comment on task "{task.title}".',
            )


        return {
            "id": comment.id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at,
        }



    async def delete_comment(
        self,
        comment_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ):
        comment = await self.comment_repo.get_by_id(
            comment_id
        )

        if not comment:
            raise CommentNotFoundException()


        if comment.user_id != current_user_id:
            raise CommentForbiddenException()


        await self.comment_repo.soft_delete(
            comment_id
        )

        return None