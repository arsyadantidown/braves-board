import uuid
import pytest

@pytest.mark.anyio
async def test_create_column_empty_title_should_fail(client):

    response = await client.post(
        "/api/v1/columns",
        json={
            "title": "",
            "board_id": str(uuid.uuid4())
        },
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422

@pytest.mark.anyio
async def test_update_column_empty_title_should_fail(client):

    response = await client.patch(
        "/api/v1/columns/test-id",
        json={"title": ""},
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422

@pytest.mark.anyio
async def test_update_column_whitespace_title_should_fail(client):

    response = await client.patch(
        "/api/v1/columns/test-id",
        json={"title": "   "},
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code == 422

@pytest.mark.anyio
async def test_reorder_column_negative_position_should_fail(client):

    response = await client.patch(
        "/api/v1/columns/test-id/reorder",
        params={"new_position": -1},
        headers={
            "X-Request-Nonce": str(uuid.uuid4())
        }
    )

    assert response.status_code in (400, 422)

@pytest.mark.anyio
async def test_get_columns_invalid_board_should_fail(client):

    response = await client.get(
        "/api/v1/columns",
        params={"board_id": str(uuid.uuid4())}
    )

    assert response.status_code in (400, 404)