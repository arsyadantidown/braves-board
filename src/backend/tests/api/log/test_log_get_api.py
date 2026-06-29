import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.api.log.schema import LogListData, LogEntryData


@pytest.fixture
def mock_log_use_case():
    mock = MagicMock()
    mock.get_logs = AsyncMock()
    return mock


@pytest.fixture
def sample_log_entry():
    return LogEntryData(
        id=1,
        timestamp=datetime.now(timezone.utc),
        log_type="http",
        level="INFO",
        logger_name="app.middleware.access_log",
        message="GET /api/v1/boards 200",
        user_id=uuid.uuid4(),
        request_id="req-abc-123",
        method="GET",
        path="/api/v1/boards",
        status_code=200,
        duration_ms=45.2,
        ip_address="127.0.0.1",
        user_agent="TestClient/1.0",
    )


@pytest.mark.anyio
async def test_get_logs_success(client: AsyncClient, mock_log_use_case, sample_log_entry):
    mock_log_use_case.get_logs.return_value = LogListData(
        logs=[sample_log_entry],
        total=1,
        page=1,
        page_size=50,
        total_pages=1,
    )

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get("/api/v1/logs/")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert len(body["data"]["logs"]) == 1


@pytest.mark.anyio
async def test_get_logs_empty_result(client: AsyncClient, mock_log_use_case):
    mock_log_use_case.get_logs.return_value = LogListData(
        logs=[],
        total=0,
        page=1,
        page_size=50,
        total_pages=0,
    )

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get("/api/v1/logs/")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 0
    assert body["data"]["logs"] == []


@pytest.mark.anyio
async def test_get_logs_with_filters(client: AsyncClient, mock_log_use_case, sample_log_entry):
    mock_log_use_case.get_logs.return_value = LogListData(
        logs=[sample_log_entry],
        total=1,
        page=1,
        page_size=50,
        total_pages=1,
    )

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get(
            "/api/v1/logs/",
            params={
                "log_type": "http",
                "level": "INFO",
                "page": 1,
                "page_size": 10,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1


@pytest.mark.anyio
async def test_get_logs_with_date_range(client: AsyncClient, mock_log_use_case):
    mock_log_use_case.get_logs.return_value = LogListData(
        logs=[],
        total=0,
        page=1,
        page_size=50,
        total_pages=0,
    )

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get(
            "/api/v1/logs/",
            params={
                "start": "2026-01-01T00:00:00Z",
                "end": "2026-12-31T23:59:59Z",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True


@pytest.mark.anyio
async def test_get_logs_with_user_id_filter(client: AsyncClient, mock_log_use_case):
    mock_log_use_case.get_logs.return_value = LogListData(
        logs=[],
        total=0,
        page=1,
        page_size=50,
        total_pages=0,
    )

    user_id = str(uuid.uuid4())

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get(
            "/api/v1/logs/",
            params={"user_id": user_id},
        )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_logs_invalid_page_size_too_large(client: AsyncClient, mock_log_use_case):
    mock_log_use_case.get_logs.return_value = LogListData(
        logs=[],
        total=0,
        page=1,
        page_size=200,
        total_pages=0,
    )

    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get(
            "/api/v1/logs/",
            params={"page_size": 999},
        )

    # FastAPI Query(ge=1, le=200) will reject values > 200
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_logs_invalid_page_zero(client: AsyncClient, mock_log_use_case):
    with patch("app.api.log.views.LogRepository"), \
         patch("app.api.log.views.LogUseCase", return_value=mock_log_use_case):
        response = await client.get(
            "/api/v1/logs/",
            params={"page": 0},
        )

    # FastAPI Query(ge=1) will reject page < 1
    assert response.status_code == 422
