import uuid
import pytest


@pytest.mark.anyio
async def test_add_attachment_link_invalid_task_id_should_fail(client):

    response = await client.post(
        "/api/v1/tasks/DummyQA/attachments/link",
        json={
            "title": "Google",
            "url": "https://www.google.com"
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_add_attachment_link_empty_url_should_fail(client):

    response = await client.post(
        f"/api/v1/tasks/{uuid.uuid4()}/attachments/link",
        json={
            "title": "Google",
            "url": ""
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_add_attachment_link_whitespace_url_should_fail(client):

    response = await client.post(
        f"/api/v1/tasks/{uuid.uuid4()}/attachments/link",
        json={
            "title": "Google",
            "url": "   "
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422