import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.api.log.schema import LogStatsData, LevelCountData, TypeCountData


@pytest.fixture
def mock_log_use_case():
    mock = MagicMock()
    mock.get_stats = AsyncMock()
    return mock


@pytest.fixture
def sample_stats():
    return LogStatsData(
        total_count=100,
        level_counts=[
            LevelCountData(level="INFO", count=70),
            LevelCountData(level="WARNING", count=20),
            LevelCountData(level="ERROR", count=8),
            LevelCountData(level="CRITICAL", count=2),
        ],
        type_counts=[
            TypeCountData(log_type="http", count=60),
            TypeCountData(log_type="application", count=30),
            TypeCountData(log_type="audit", count=10),
        ],
        error_rate=10.0,
        start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end=datetime(2026, 12, 31, tzinfo=timezone.utc),
    )


@pytest.mark.anyio
async def test_get_log_stats_success(client: AsyncClient, mock_log_use_case, sample_stats):
    mock_log_use_case.get_stats.return_value = sample_stats

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get("/api/v1/logs/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total_count"] == 100
    assert body["data"]["error_rate"] == 10.0
    assert len(body["data"]["level_counts"]) == 4
    assert len(body["data"]["type_counts"]) == 3


@pytest.mark.anyio
async def test_get_log_stats_empty(client: AsyncClient, mock_log_use_case):
    mock_log_use_case.get_stats.return_value = LogStatsData(
        total_count=0,
        level_counts=[],
        type_counts=[],
        error_rate=0.0,
        start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end=datetime(2026, 12, 31, tzinfo=timezone.utc),
    )

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get("/api/v1/logs/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total_count"] == 0
    assert body["data"]["level_counts"] == []
    assert body["data"]["type_counts"] == []
    assert body["data"]["error_rate"] == 0.0


@pytest.mark.anyio
async def test_get_log_stats_with_date_range(client: AsyncClient, mock_log_use_case, sample_stats):
    mock_log_use_case.get_stats.return_value = sample_stats

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get(
            "/api/v1/logs/stats",
            params={
                "start": "2026-06-01T00:00:00Z",
                "end": "2026-06-30T23:59:59Z",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total_count"] == 100
