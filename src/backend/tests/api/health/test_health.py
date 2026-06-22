import pytest


@pytest.mark.anyio
async def test_liveness_check(client):

    response = await client.get("/api/v1/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "message": "Application is alive",
    }