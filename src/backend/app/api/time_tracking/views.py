import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.models.user_model import User

from app.api.time_tracking.schema import (
    TimerPayload,
    TimerStopPayload,
)
from app.api.time_tracking.use_cases import TimeTrackingUseCase
from app.api.standard_response import success_response

from app.core.dependencies import require_permission


router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["Task Timer"]
)


def get_time_tracking_use_case(
    db: AsyncSession = Depends(get_db)
) -> TimeTrackingUseCase:
    return TimeTrackingUseCase(db)


@router.post(
    "/timers/cleanup",
    status_code=status.HTTP_200_OK
)
async def system_cleanup(
    use_case: TimeTrackingUseCase = Depends(
        get_time_tracking_use_case
    )
):
    result = await use_case.run_cleanup()
    return success_response(result)


@router.post(
    "/{task_id}/timer/start",
    status_code=status.HTTP_200_OK
)
async def start_timer(
    task_id: uuid.UUID,
    payload: TimerPayload | None = None,
    use_case: TimeTrackingUseCase = Depends(
        get_time_tracking_use_case
    ),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    description = payload.description if payload else None

    result = await use_case.start_timer(
        task_id,
        description
    )

    return success_response(result)


@router.post(
    "/{task_id}/timer/stop",
    status_code=status.HTTP_200_OK
)
async def stop_timer(
    task_id: uuid.UUID,
    payload: TimerStopPayload | None = None,
    use_case: TimeTrackingUseCase = Depends(
        get_time_tracking_use_case
    ),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    reason = payload.reason if payload else "manual"

    result = await use_case.stop_timer(
        task_id,
        reason
    )

    return success_response(result)


@router.post(
    "/{task_id}/timer/ping",
    status_code=status.HTTP_200_OK
)
async def ping_timer(
    task_id: uuid.UUID,
    use_case: TimeTrackingUseCase = Depends(
        get_time_tracking_use_case
    ),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.ping(task_id)

    return success_response(result)


@router.post(
    "/{task_id}/timer/confirm",
    status_code=status.HTTP_200_OK
)
async def confirm_timer(
    task_id: uuid.UUID,
    use_case: TimeTrackingUseCase = Depends(
        get_time_tracking_use_case
    ),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    result = await use_case.confirm(task_id)

    return success_response(result)


@router.get(
    "/{task_id}/timer/logs",
    status_code=status.HTTP_200_OK
)
async def get_time_logs(
    task_id: uuid.UUID,
    use_case: TimeTrackingUseCase = Depends(
        get_time_tracking_use_case
    ),
    current_user: User = Depends(
        require_permission("task.view")
    ),
):
    result = await use_case.get_time_logs(task_id)

    return success_response(result)