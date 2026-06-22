import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.api.column.views import get_column_use_case
from app.api.exceptions.column_exceptions import ColumnNotFoundException

@pytest.fixture
def mock_column_use_case():
    mock = MagicMock()
    mock.delete_column = AsyncMock()
    return mock

@pytest.mark.anyio
async def test_delete_column_success(client: AsyncClient, mock_column_use_case):
    mock_column_use_case.delete_column.return_value = None
    app.dependency_overrides[get_column_use_case] = lambda: mock_column_use_case
    
    column_id = "00000000-0000-0000-0000-000000000000"

    response = await client.delete(
        f"/api/v1/columns/{column_id}",
        headers={"X-Request-Nonce": str(uuid.uuid4())}
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200


@pytest.mark.anyio
async def test_delete_column_not_found_should_not_crash(client: AsyncClient, mock_column_use_case):
    mock_column_use_case.delete_column.side_effect = ColumnNotFoundException()
    app.dependency_overrides[get_column_use_case] = lambda: mock_column_use_case
    
    column_id = "11111111-1111-1111-1111-111111111111"

    response = await client.delete(
        f"/api/v1/columns/{column_id}",
        headers={"X-Request-Nonce": str(uuid.uuid4())}
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404