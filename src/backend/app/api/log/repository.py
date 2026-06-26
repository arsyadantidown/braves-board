import uuid
import math
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_log_model import AppLog


class LogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_logs(
        self,
        log_type: Optional[str] = None,
        level: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        request_id: Optional[str] = None,
        action: Optional[str] = None,
        path: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AppLog], int]:
        """
        Query logs with filters and pagination.
        Returns a tuple of (logs, total_count).
        """
        # Default time range: last 24 hours
        if end is None:
            end = datetime.now(timezone.utc)
        if start is None:
            start = end - timedelta(hours=24)

        # Build filter conditions
        conditions = [
            AppLog.timestamp >= start,
            AppLog.timestamp <= end,
        ]

        if log_type:
            conditions.append(AppLog.log_type == log_type)
        if level:
            conditions.append(AppLog.level == level)
        if user_id:
            conditions.append(AppLog.user_id == user_id)
        if request_id:
            conditions.append(AppLog.request_id == request_id)
        if action:
            conditions.append(AppLog.action == action)
        if path:
            conditions.append(AppLog.path.ilike(f"%{path}%"))

        where_clause = and_(*conditions)

        # Count total
        count_stmt = select(func.count()).select_from(AppLog).where(where_clause)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Fetch paginated results
        offset = (page - 1) * page_size
        query_stmt = (
            select(AppLog)
            .where(where_clause)
            .order_by(AppLog.timestamp.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.session.execute(query_stmt)
        logs = list(result.scalars().all())

        return logs, total

    async def get_stats(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> dict:
        """
        Get log statistics for a time range.
        Returns counts per level, per type, and error rate.
        """
        if end is None:
            end = datetime.now(timezone.utc)
        if start is None:
            start = end - timedelta(hours=24)

        time_filter = and_(
            AppLog.timestamp >= start,
            AppLog.timestamp <= end,
        )

        # Total count
        total_stmt = select(func.count()).select_from(AppLog).where(time_filter)
        total_result = await self.session.execute(total_stmt)
        total_count = total_result.scalar_one()

        # Count per level
        level_stmt = (
            select(AppLog.level, func.count().label("count"))
            .where(time_filter)
            .group_by(AppLog.level)
            .order_by(func.count().desc())
        )
        level_result = await self.session.execute(level_stmt)
        level_counts = [
            {"level": row.level, "count": row.count}
            for row in level_result.all()
        ]

        # Count per log_type
        type_stmt = (
            select(AppLog.log_type, func.count().label("count"))
            .where(time_filter)
            .group_by(AppLog.log_type)
            .order_by(func.count().desc())
        )
        type_result = await self.session.execute(type_stmt)
        type_counts = [
            {"log_type": row.log_type, "count": row.count}
            for row in type_result.all()
        ]

        # Error rate
        error_count = sum(
            lc["count"] for lc in level_counts
            if lc["level"] in ("ERROR", "CRITICAL")
        )
        error_rate = (error_count / total_count * 100) if total_count > 0 else 0.0

        return {
            "total_count": total_count,
            "level_counts": level_counts,
            "type_counts": type_counts,
            "error_rate": round(error_rate, 2),
            "start": start,
            "end": end,
        }
