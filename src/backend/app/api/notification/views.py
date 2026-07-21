import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.notification.repository import NotificationRepository
from app.api.notification.use_cases import NotificationUseCase
from app.api.depedencies import get_current_user
from app.api.standard_response import success_response
from app.models.user_model import User


router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


def get_notification_use_case(
    db: AsyncSession = Depends(get_db),
) -> NotificationUseCase:
    repo = NotificationRepository(db)
    return NotificationUseCase(repo)


@router.get("", status_code=status.HTTP_200_OK)
async def get_notifications(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case: NotificationUseCase = Depends(get_notification_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.get_all(current_user.id, limit, offset)
    return success_response(result)


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    use_case: NotificationUseCase = Depends(get_notification_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.mark_as_read(notification_id, current_user.id)
    return success_response(result)


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
async def delete_notification(
    notification_id: uuid.UUID,
    use_case: NotificationUseCase = Depends(get_notification_use_case),
    current_user: User = Depends(get_current_user),
):
    await use_case.delete(notification_id, current_user.id)
    return success_response(None)

@router.get("/unread-count")
async def get_unread_count(
    use_case: NotificationUseCase = Depends(get_notification_use_case),
    current_user: User = Depends(get_current_user),
):

    result = await use_case.get_unread_count(
        current_user.id
    )

    return success_response(result)

@router.patch("/read-all")
async def mark_all_read(
    use_case: NotificationUseCase = Depends(get_notification_use_case),
    current_user: User = Depends(get_current_user),
):

    result = await use_case.mark_all_as_read(
        current_user.id
    )

    return success_response(result)