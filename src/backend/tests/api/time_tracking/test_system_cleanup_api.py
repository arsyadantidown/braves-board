import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.api.time_tracking.views import get_time_tracking_use_case

@pytest.fixture
def mock_use_case():
    mock = MagicMock()
    mock.run_cleanup = AsyncMock(return_value={"cleaned": 5})
    return mock

@pytest.mark.anyio
async def test_system_cleanup_success(client: AsyncClient, mock_use_case):
    app.dependency_overrides[get_time_tracking_use_case] = lambda: mock_use_case
    
    response = await client.post(
        "/api/v1/tasks/timers/cleanup",
        headers={"X-Request-Nonce": str(uuid.uuid4())}
    )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["cleaned"] == 5
