import math
from app.api.log.repository import LogRepository
from app.api.log.schema import (
    LogEntryData,
    LogListData,
    LogStatsData,
    LogQueryParams,
    LevelCountData,
    TypeCountData,
)


class LogUseCase:
    def __init__(self, log_repo: LogRepository):
        self.log_repo = log_repo

    async def get_logs(self, params: LogQueryParams) -> LogListData:
        """Get filtered and paginated log entries."""
        logs, total = await self.log_repo.get_logs(
            log_type=params.log_type,
            level=params.level,
            user_id=params.user_id,
            request_id=params.request_id,
            action=params.action,
            path=params.path,
            start=params.start,
            end=params.end,
            page=params.page,
            page_size=params.page_size,
        )

        total_pages = math.ceil(total / params.page_size) if total > 0 else 0

        return LogListData(
            logs=[LogEntryData.model_validate(log) for log in logs],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )

    async def get_stats(self, params: LogQueryParams) -> LogStatsData:
        """Get log statistics for a time range."""
        stats = await self.log_repo.get_stats(
            start=params.start,
            end=params.end,
        )

        return LogStatsData(
            total_count=stats["total_count"],
            level_counts=[
                LevelCountData(**lc) for lc in stats["level_counts"]
            ],
            type_counts=[
                TypeCountData(**tc) for tc in stats["type_counts"]
            ],
            error_rate=stats["error_rate"],
            start=stats["start"],
            end=stats["end"],
        )
