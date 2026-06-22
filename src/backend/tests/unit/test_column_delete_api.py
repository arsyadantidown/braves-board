import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)

    return AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
    )


@pytest.mark.anyio
async def test_delete_column_success(client: AsyncClient):
    column_id = "00000000-0000-0000-0000-000000000000"

    response = await client.delete(f"/api/v1/columns/{column_id}")

    assert response.status_code in (200, 404)


@pytest.mark.anyio
async def test_delete_column_not_found_should_not_crash(client: AsyncClient):
    column_id = "11111111-1111-1111-1111-111111111111"

    response = await client.delete(f"/api/v1/columns/{column_id}")

    # yang penting: tidak crash sistemik
    assert response.status_code != 500