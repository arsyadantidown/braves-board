import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.models.user_model import User

from app.api.subtask.use_cases import SubtaskUseCase
from app.api.subtask.schema import (
    SubtaskCreateRequest,
    SubtaskUpdateRequest,
    SubtaskCompleteRequest,
    SubtaskMoveRequest,
)

from app.api.standard_response import success_response
from app.core.dependencies import require_permission


router = APIRouter(
    prefix="/api/v1",
    tags=["Subtasks"]
)


def get_subtask_use_case(
    db: AsyncSession = Depends(get_db)
) -> SubtaskUseCase:
    return SubtaskUseCase(db)


@router.post(
    "/tasks/{task_id}/subtasks",
    status_code=status.HTTP_201_CREATED
)
async def create_subtask(
    task_id: uuid.UUID,
    payload: SubtaskCreateRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.create_subtask(
        task_id,
        payload
    )

    return success_response(result)


@router.patch(
    "/subtasks/{subtask_id}",
    status_code=status.HTTP_200_OK
)
async def update_subtask(
    subtask_id: uuid.UUID,
    payload: SubtaskUpdateRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.update_subtask(
        subtask_id,
        payload
    )

    return success_response(result)


@router.patch(
    "/subtasks/{subtask_id}/complete",
    status_code=status.HTTP_200_OK
)
async def complete_subtask(
    subtask_id: uuid.UUID,
    payload: SubtaskCompleteRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.complete_subtask(
        subtask_id,
        payload
    )

    return success_response(result)


@router.patch(
    "/subtasks/{subtask_id}/move",
    status_code=status.HTTP_200_OK
)
async def move_subtask(
    subtask_id: uuid.UUID,
    payload: SubtaskMoveRequest,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.move_subtask(
        subtask_id,
        payload
    )

    return success_response(result)


@router.delete(
    "/subtasks/{subtask_id}",
    status_code=status.HTTP_200_OK
)
async def delete_subtask(
    subtask_id: uuid.UUID,
    use_case: SubtaskUseCase = Depends(get_subtask_use_case),
    current_user: User = Depends(
        require_permission("task.delete")
    ),
):
    await use_case.delete_subtask(
        subtask_id
    )

    return success_response(
        {"message": "Subtask berhasil dihapus"}
    )