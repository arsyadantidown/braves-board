import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.task.schema import TaskCreateRequest, TaskUpdateRequest, TaskMoveRequest, TaskReorderRequest
from app.api.task.use_cases import TaskUseCase
from app.api.depedencies import get_current_user
from app.models.user_model import User
from app.api.standard_response import success_response
from app.api.exceptions.task_exceptions import InvalidUUIDFormatException

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

def get_task_use_case(db: AsyncSession = Depends(get_db)) -> TaskUseCase:
    return TaskUseCase(db)

def validate_uuid(id_str: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(id_str))
    except ValueError:
        raise InvalidUUIDFormatException()

@router.get("", status_code=status.HTTP_200_OK)
async def get_tasks(
    column_id: str,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_column_id = validate_uuid(column_id)
    result = await use_case.get_tasks_by_column(valid_column_id)
    return success_response(result)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreateRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(get_current_user)
):
    result = await use_case.create_task(request)
    return success_response(result)

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_task_detail(
    id: str,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(id)
    result = await use_case.get_task_detail(valid_id)
    return success_response(result)

@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def update_task(
    id: str,
    request: TaskUpdateRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(id)
    result = await use_case.update_task(valid_id, request)
    return success_response(result)

@router.patch("/{id}/move", status_code=status.HTTP_200_OK)
async def move_task(
    id: str,
    request: TaskMoveRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(id)
    result = await use_case.move_task(valid_id, request)
    return success_response(result)

@router.patch("/{id}/reorder", status_code=status.HTTP_200_OK)
async def reorder_task(
    id: str,
    request: TaskReorderRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(id)
    result = await use_case.reorder_task(valid_id, request)
    return success_response(result)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_task(
    id: str,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(id)
    await use_case.delete_task(valid_id)
    return success_response(None)