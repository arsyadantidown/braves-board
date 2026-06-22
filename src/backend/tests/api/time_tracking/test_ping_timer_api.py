import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.api.time_tracking.views import get_time_tracking_use_case

@pytest.fixture
def mock_use_case():
    mock = MagicMock()
    mock.ping = AsyncMock(return_value={"status": "active"})
    return mock

@pytest.mark.anyio
async def test_ping_timer_success(client: AsyncClient, mock_use_case):
    app.dependency_overrides[get_time_tracking_use_case] = lambda: mock_use_case
    
    task_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/tasks/{task_id}/timer/ping",
        headers={"X-Request-Nonce": str(uuid.uuid4())}
    )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "active"
