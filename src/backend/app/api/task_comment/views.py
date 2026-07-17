import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.task_comment.schema import AddCommentRequest
from app.api.task_comment.use_cases import TaskCommentUseCase
from app.models.user_model import User
from app.api.standard_response import success_response

from app.core.dependencies import require_permission


router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["Task Comments"]
)


def get_task_comment_use_case(
    db: AsyncSession = Depends(get_db)
) -> TaskCommentUseCase:
    return TaskCommentUseCase(db)


@router.post(
    "/{id}/comments",
    status_code=status.HTTP_201_CREATED
)
async def add_comment(
    id: uuid.UUID,
    request: AddCommentRequest,
    use_case: TaskCommentUseCase = Depends(
        get_task_comment_use_case
    ),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.add_comment(
        task_id=id,
        content=request.content,
        current_user_id=current_user.id,
    )

    return success_response(result)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_200_OK
)
async def delete_comment(
    comment_id: uuid.UUID,
    use_case: TaskCommentUseCase = Depends(
        get_task_comment_use_case
    ),
    current_user: User = Depends(
        require_permission("task.delete")
    ),
):
    await use_case.delete_comment(
        comment_id=comment_id,
        current_user_id=current_user.id,
    )

    return success_response(None)