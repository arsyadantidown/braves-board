import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.depedencies import get_current_user
from app.api.standard_response import StandardResponse, success_response
from app.api.log.schema import LogListData, LogStatsData, LogQueryParams
from app.api.log.repository import LogRepository
from app.api.log.use_cases import LogUseCase
from app.models.user_model import User

router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])


@router.get("/", response_model=StandardResponse[LogListData])
async def get_logs(
    log_type: Optional[str] = Query(default=None, description="Filter by log type: 'http', 'application', 'audit'"),
    level: Optional[str] = Query(default=None, description="Filter by level: 'INFO', 'WARNING', 'ERROR', 'CRITICAL'"),
    user_id: Optional[uuid.UUID] = Query(default=None, description="Filter by user ID"),
    request_id: Optional[str] = Query(default=None, description="Filter by request ID"),
    action: Optional[str] = Query(default=None, description="Filter by audit action (e.g. 'board.create')"),
    path: Optional[str] = Query(default=None, description="Filter by request path (partial match)"),
    start: Optional[datetime] = Query(default=None, description="Start datetime (ISO 8601)"),
    end: Optional[datetime] = Query(default=None, description="End datetime (ISO 8601)"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=200, description="Items per page (max 200)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get filtered and paginated log entries."""
    params = LogQueryParams(
        log_type=log_type,
        level=level,
        user_id=user_id,
        request_id=request_id,
        action=action,
        path=path,
        start=start,
        end=end,
        page=page,
        page_size=page_size,
    )

    log_repo = LogRepository(db)
    use_case = LogUseCase(log_repo)
    result = await use_case.get_logs(params)

    return success_response(result)


@router.get("/stats", response_model=StandardResponse[LogStatsData])
async def get_log_stats(
    start: Optional[datetime] = Query(default=None, description="Start datetime (ISO 8601)"),
    end: Optional[datetime] = Query(default=None, description="End datetime (ISO 8601)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get log statistics for a time range."""
    params = LogQueryParams(start=start, end=end)

    log_repo = LogRepository(db)
    use_case = LogUseCase(log_repo)
    result = await use_case.get_stats(params)

    return success_response(result)
