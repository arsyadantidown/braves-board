import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.depedencies import get_current_user
from app.models.user_model import User
from app.api.subtask.use_cases import SubtaskUseCase
from app.api.subtask.schema import (
    SubtaskCreateRequest,
    SubtaskUpdateRequest,
    SubtaskCompleteRequest,
    SubtaskMoveRequest,
)
from app.api.standard_response import success_response
from app.api.exceptions.task_exceptions import InvalidUUIDFormatException

router = APIRouter(prefix="/api/v1", tags=["Subtasks"])

def get_subtask_use_case(db: AsyncSession = Depends(get_db)) -> SubtaskUseCase:
    return SubtaskUseCase(db)

def validate_uuid(id_str: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(id_str))
    except ValueError:
        raise InvalidUUIDFormatException()

@router.post("/tasks/{task_id}/subtasks", status_code=status.HTTP_201_CREATED)
async def create_subtask(
    task_id: str,
    payload: SubtaskCreateRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_task_id = validate_uuid(task_id)
    result = await use_case.create_subtask(valid_task_id, payload)
    return success_response(result)

@router.patch("/subtasks/{subtask_id}", status_code=status.HTTP_200_OK)
async def update_subtask(
    subtask_id: str,
    payload: SubtaskUpdateRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(subtask_id)
    result = await use_case.update_subtask(valid_id, payload)
    return success_response(result)

@router.patch("/subtasks/{subtask_id}/complete", status_code=status.HTTP_200_OK)
async def complete_subtask(
    subtask_id: str,
    payload: SubtaskCompleteRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(subtask_id)
    result = await use_case.complete_subtask(valid_id, payload)
    return success_response(result)

@router.patch("/subtasks/{subtask_id}/move", status_code=status.HTTP_200_OK)
async def move_subtask(
    subtask_id: str,
    payload: SubtaskMoveRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(subtask_id)
    result = await use_case.move_subtask(valid_id, payload)
    return success_response(result)

@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_200_OK)
async def delete_subtask(
    subtask_id: str,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(get_current_user)
):
    valid_id = validate_uuid(subtask_id)
    await use_case.delete_subtask(valid_id)
    return success_response({"message": "Subtask berhasil dihapus"})