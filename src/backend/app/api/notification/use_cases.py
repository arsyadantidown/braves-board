import uuid

from app.models.notification_model import Notification
from app.api.notification.repository import NotificationRepository
from app.api.exceptions.notification_exceptions import (
    NotificationNotFoundException,
)


class NotificationUseCase:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def _notification_to_dict(self, notification: Notification) -> dict:
        return {
            "id": str(notification.id),
            "user_id": str(notification.user_id),
            "board_id": str(notification.board_id),
            "task_id": str(notification.task_id) if notification.task_id else None,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
        }

    async def get_all(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        notifications = await self.repo.get_all(user_id, limit, offset)

        return {
            "notifications": [
                self._notification_to_dict(notification)
                for notification in notifications
            ],
            "meta": {
                "limit": limit,
                "offset": offset,
                "count": len(notifications),
            },
        }

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        board_id: uuid.UUID,
        task_id: uuid.UUID | None = None,
        type: str,
        title: str,
        message: str,
    ) -> dict:
        notification = Notification(
            user_id=user_id,
            board_id=board_id,
            task_id=task_id,
            type=type,
            title=title,
            message=message,
        )

        notification = await self.repo.create(notification)

        return self._notification_to_dict(notification)

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        notification = await self.repo.mark_as_read(notification_id, user_id)

        if not notification:
            raise NotificationNotFoundException()

        return self._notification_to_dict(notification)

    async def delete(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        success = await self.repo.delete(notification_id, user_id)

        if not success:
            raise NotificationNotFoundException()

        return None

    async def get_unread_count(
        self,
        user_id: uuid.UUID,
    ):

        count = await self.repo.get_unread_count(user_id)

        return {
            "count": count
        }
    
    async def mark_all_as_read(
        self,
        user_id: uuid.UUID,
    ):

        await self.repo.mark_all_as_read(user_id)

        return {
            "message": "All notifications marked as read"
        }