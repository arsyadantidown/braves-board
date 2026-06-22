import uuid
import pytest


@pytest.mark.anyio
async def test_create_comment_empty_content_should_fail(client):

    response = await client.post(
        f"/api/v1/tasks/{uuid.uuid4()}/comments",
        json={
            "content": ""
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_comment_whitespace_content_should_fail(client):

    response = await client.post(
        f"/api/v1/tasks/{uuid.uuid4()}/comments",
        json={
            "content": "   "
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422