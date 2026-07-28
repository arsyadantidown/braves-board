import uuid
from typing import Sequence

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_model import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification | None:
        stmt = (
            select(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, user_id: uuid.UUID, limit: int, offset: int) -> Sequence[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification | None:
        stmt = (
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True)
            .returning(Notification)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = (
            delete(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_unread_count(
        self,
        user_id: uuid.UUID,
    ) -> int:

        stmt = (
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar()    