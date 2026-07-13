import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.task.schema import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskMoveRequest,
    TaskReorderRequest,
)
from app.api.task.use_cases import TaskUseCase
from app.models.user_model import User
from app.api.standard_response import success_response

from app.core.dependencies import require_permission


router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


def get_task_use_case(
    db: AsyncSession = Depends(get_db)
) -> TaskUseCase:
    return TaskUseCase(db)


@router.get("", status_code=status.HTTP_200_OK)
async def get_tasks(
    column_id: uuid.UUID,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(
        require_permission("task.view")
    ),
):
    result = await use_case.get_tasks_by_column(
        column_id
    )
    return success_response(result)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreateRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(
        require_permission("task.create")
    ),
):
    result = await use_case.create_task(payload)
    return success_response(result)


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_detail(
    task_id: uuid.UUID,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(
        require_permission("task.view")
    ),
):
    result = await use_case.get_task_detail(
        task_id
    )
    return success_response(result)


@router.patch("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdateRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.update_task(
        task_id,
        payload,
    )
    return success_response(result)


@router.patch("/{task_id}/move", status_code=status.HTTP_200_OK)
async def move_task(
    task_id: uuid.UUID,
    payload: TaskMoveRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.move_task(
        task_id,
        payload,
    )
    return success_response(result)


@router.patch("/{task_id}/reorder", status_code=status.HTTP_200_OK)
async def reorder_task(
    task_id: uuid.UUID,
    payload: TaskReorderRequest,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.reorder_task(
        task_id,
        payload,
    )
    return success_response(result)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: uuid.UUID,
    use_case: TaskUseCase = Depends(get_task_use_case),
    current_user: User = Depends(
        require_permission("task.delete")
    ),
):
    await use_case.delete_task(
        task_id
    )
    return success_response(None)