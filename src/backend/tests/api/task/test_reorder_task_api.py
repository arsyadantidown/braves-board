import uuid
import pytest


@pytest.mark.anyio
async def test_reorder_task_negative_position_should_fail(client):

    response = await client.patch(
        f"/api/v1/tasks/{uuid.uuid4()}/reorder",
        json={
            "position": -1
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_reorder_task_zero_position_should_fail(client):

    response = await client.patch(
        f"/api/v1/tasks/{uuid.uuid4()}/reorder",
        json={
            "position": 0
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422