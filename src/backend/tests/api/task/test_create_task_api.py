import uuid
import pytest


@pytest.mark.anyio
async def test_create_task_empty_title_should_fail(client):

    response = await client.post(
        "/api/v1/tasks",
        json={
            "column_id": str(uuid.uuid4()),
            "title": "",
            "assignee_ids": []
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_task_whitespace_title_should_fail(client):

    response = await client.post(
        "/api/v1/tasks",
        json={
            "column_id": str(uuid.uuid4()),
            "title": "   ",
            "assignee_ids": []
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422