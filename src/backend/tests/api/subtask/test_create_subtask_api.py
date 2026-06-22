import uuid
import pytest


@pytest.mark.anyio
async def test_update_subtask_empty_title_should_fail(client):

    response = await client.patch(
        f"/api/v1/subtasks/{uuid.uuid4()}",
        json={
            "title": ""
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_update_subtask_whitespace_title_should_fail(client):

    response = await client.patch(
        f"/api/v1/subtasks/{uuid.uuid4()}",
        json={
            "title": "   "
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422