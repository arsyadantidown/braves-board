import uuid
import pytest


@pytest.mark.anyio
async def test_delete_attachment_invalid_id_should_fail(client):

    response = await client.delete(
        "/api/v1/tasks/attachments/test",
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_delete_attachment_invalid_id_whitespace_should_fail(client):

    response = await client.delete(
        "/api/v1/tasks/attachments/   ",
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422