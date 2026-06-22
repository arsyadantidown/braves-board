import io
import uuid
import pytest


@pytest.mark.anyio
async def test_upload_attachment_invalid_task_id_should_fail(client):

    file = io.BytesIO(b"fake image")
    file.name = "test.png"

    response = await client.post(
        "/api/v1/tasks/pgAdmin/attachments/file",
        files={
            "file": (
                "test.png",
                file,
                "image/png"
            )
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_upload_attachment_without_file_should_fail(client):

    response = await client.post(
        f"/api/v1/tasks/{uuid.uuid4()}/attachments/file",
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422