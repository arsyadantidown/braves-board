import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.connections.postgres import get_db
from app.api.task_comment.schema import AddCommentRequest
from app.api.task_comment.use_cases import TaskCommentUseCase
from app.api.depedencies import get_current_user
from app.models.user_model import User
from app.api.standard_response import success_response
from app.api.exceptions.task_exceptions import InvalidUUIDFormatException

router = APIRouter(prefix="/api/v1/tasks", tags=["Task Comments"])

def get_task_comment_use_case(db: AsyncSession = Depends(get_db)) -> TaskCommentUseCase:
    return TaskCommentUseCase(db)

def validate_uuid(id_str: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(id_str))
    except ValueError:
        raise InvalidUUIDFormatException()

@router.post("/{id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    id: str,
    request: AddCommentRequest,
    use_case: TaskCommentUseCase = Depends(get_task_comment_use_case),
    current_user: User = Depends(get_current_user),
):
    valid_id = validate_uuid(id)
    result = await use_case.add_comment(
        task_id=valid_id,
        content=request.content,
        current_user_id=current_user.id,
    )
    return success_response(result)

@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    comment_id: str,
    use_case: TaskCommentUseCase = Depends(get_task_comment_use_case),
    current_user: User = Depends(get_current_user),
):
    valid_id = validate_uuid(comment_id)
    await use_case.delete_comment(
        comment_id=valid_id,
        current_user_id=current_user.id,
    )
    return success_response(None)