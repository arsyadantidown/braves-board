import uuid
import math
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.api.log.use_cases import LogUseCase
from app.api.log.schema import LogQueryParams, LogListData, LogStatsData


@pytest.fixture
def mock_log_repo():
    return MagicMock()


@pytest.fixture
def log_use_case(mock_log_repo):
    return LogUseCase(mock_log_repo)


@pytest.mark.anyio
async def test_get_logs_returns_paginated_result(log_use_case, mock_log_repo):
    fake_log = MagicMock()
    fake_log.id = 1
    fake_log.timestamp = datetime.now(timezone.utc)
    fake_log.log_type = "http"
    fake_log.level = "INFO"
    fake_log.logger_name = "app.access"
    fake_log.message = "GET /api/v1/boards 200"
    fake_log.user_id = None
    fake_log.request_id = "req-1"
    fake_log.method = "GET"
    fake_log.path = "/api/v1/boards"
    fake_log.status_code = 200
    fake_log.duration_ms = 35.0
    fake_log.ip_address = "127.0.0.1"
    fake_log.user_agent = "TestClient"
    fake_log.action = None
    fake_log.resource_type = None
    fake_log.resource_id = None
    fake_log.extra = None

    mock_log_repo.get_logs = AsyncMock(return_value=([fake_log], 1))

    params = LogQueryParams(page=1, page_size=50)
    result = await log_use_case.get_logs(params)

    assert isinstance(result, LogListData)
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 50
    assert result.total_pages == 1
    assert len(result.logs) == 1
    assert result.logs[0].id == 1


@pytest.mark.anyio
async def test_get_logs_empty_returns_zero_pages(log_use_case, mock_log_repo):
    mock_log_repo.get_logs = AsyncMock(return_value=([], 0))

    params = LogQueryParams(page=1, page_size=50)
    result = await log_use_case.get_logs(params)

    assert isinstance(result, LogListData)
    assert result.total == 0
    assert result.total_pages == 0
    assert result.logs == []


@pytest.mark.anyio
async def test_get_logs_calculates_total_pages_correctly(log_use_case, mock_log_repo):
    mock_log_repo.get_logs = AsyncMock(return_value=([], 101))

    params = LogQueryParams(page=1, page_size=50)
    result = await log_use_case.get_logs(params)

    # 101 items / 50 per page = 3 pages (ceil)
    assert result.total_pages == 3
    assert result.total == 101


@pytest.mark.anyio
async def test_get_logs_passes_filters_to_repo(log_use_case, mock_log_repo):
    uid = uuid.uuid4()
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 12, 31, tzinfo=timezone.utc)

    mock_log_repo.get_logs = AsyncMock(return_value=([], 0))

    params = LogQueryParams(
        log_type="audit",
        level="ERROR",
        user_id=uid,
        request_id="req-xyz",
        action="board.create",
        path="/api/v1/boards",
        start=start,
        end=end,
        page=2,
        page_size=25,
    )

    await log_use_case.get_logs(params)

    mock_log_repo.get_logs.assert_called_once_with(
        log_type="audit",
        level="ERROR",
        user_id=uid,
        request_id="req-xyz",
        action="board.create",
        path="/api/v1/boards",
        start=start,
        end=end,
        page=2,
        page_size=25,
    )


@pytest.mark.anyio
async def test_get_stats_returns_stats_data(log_use_case, mock_log_repo):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 12, 31, tzinfo=timezone.utc)

    mock_log_repo.get_stats = AsyncMock(return_value={
        "total_count": 100,
        "level_counts": [
            {"level": "INFO", "count": 70},
            {"level": "ERROR", "count": 30},
        ],
        "type_counts": [
            {"log_type": "http", "count": 80},
            {"log_type": "audit", "count": 20},
        ],
        "error_rate": 30.0,
        "start": start,
        "end": end,
    })

    params = LogQueryParams(start=start, end=end)
    result = await log_use_case.get_stats(params)

    assert isinstance(result, LogStatsData)
    assert result.total_count == 100
    assert result.error_rate == 30.0
    assert len(result.level_counts) == 2
    assert result.level_counts[0].level == "INFO"
    assert result.level_counts[0].count == 70
    assert len(result.type_counts) == 2
    assert result.type_counts[0].log_type == "http"


@pytest.mark.anyio
async def test_get_stats_empty_logs(log_use_case, mock_log_repo):
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    end = datetime(2026, 6, 30, tzinfo=timezone.utc)

    mock_log_repo.get_stats = AsyncMock(return_value={
        "total_count": 0,
        "level_counts": [],
        "type_counts": [],
        "error_rate": 0.0,
        "start": start,
        "end": end,
    })

    params = LogQueryParams(start=start, end=end)
    result = await log_use_case.get_stats(params)

    assert result.total_count == 0
    assert result.level_counts == []
    assert result.type_counts == []
    assert result.error_rate == 0.0


@pytest.mark.anyio
async def test_get_stats_passes_time_range_to_repo(log_use_case, mock_log_repo):
    start = datetime(2026, 3, 1, tzinfo=timezone.utc)
    end = datetime(2026, 3, 31, tzinfo=timezone.utc)

    mock_log_repo.get_stats = AsyncMock(return_value={
        "total_count": 0,
        "level_counts": [],
        "type_counts": [],
        "error_rate": 0.0,
        "start": start,
        "end": end,
    })

    params = LogQueryParams(start=start, end=end)
    await log_use_case.get_stats(params)

    mock_log_repo.get_stats.assert_called_once_with(
        start=start,
        end=end,
    )
