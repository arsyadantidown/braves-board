import pytest
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.middleware.nonce import setup_nonce

@pytest.fixture
def app_with_nonce():
    app = FastAPI()
    setup_nonce(app)
    
    @app.post("/test")
    async def test_post():
        return {"message": "ok"}
        
    @app.get("/test")
    async def test_get():
        return {"message": "ok"}
        
    @app.post("/api/v1/auth/google/login")
    async def test_exempt():
        return {"message": "ok"}
        
    return app

@pytest.mark.anyio
async def test_nonce_exempt_path(app_with_nonce):
    async with AsyncClient(app=app_with_nonce, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/google/login")
    assert response.status_code == 200

@pytest.mark.anyio
async def test_nonce_get_method_ignored(app_with_nonce):
    async with AsyncClient(app=app_with_nonce, base_url="http://test") as client:
        response = await client.get("/test")
    assert response.status_code == 200

@pytest.mark.anyio
async def test_nonce_missing(app_with_nonce):
    async with AsyncClient(app=app_with_nonce, base_url="http://test") as client:
        with pytest.raises(HTTPException) as exc_info:
            await client.post("/test")
    assert exc_info.value.status_code == 400
    assert "X-Request-Nonce header is required" in exc_info.value.detail

@pytest.mark.anyio
@patch("app.middleware.nonce.redis_client.exists", new_callable=AsyncMock)
async def test_nonce_duplicate(mock_exists, app_with_nonce):
    mock_exists.return_value = True
    
    async with AsyncClient(app=app_with_nonce, base_url="http://test") as client:
        with pytest.raises(HTTPException) as exc_info:
            await client.post("/test", headers={"X-Request-Nonce": "duplicate123"})
        
    assert exc_info.value.status_code == 409
    assert "Replay attack detected: duplicate nonce" in exc_info.value.detail

@pytest.mark.anyio
@patch("app.middleware.nonce.redis_client.exists", new_callable=AsyncMock)
@patch("app.middleware.nonce.redis_client.pipeline")
async def test_nonce_success(mock_pipeline, mock_exists, app_with_nonce):
    mock_exists.return_value = False
    
    from unittest.mock import MagicMock
    mock_pipe = MagicMock()
    mock_pipe.execute = AsyncMock()
    mock_pipe.__aenter__ = AsyncMock(return_value=mock_pipe)
    mock_pipe.__aexit__ = AsyncMock()
    mock_pipeline.return_value = mock_pipe
    
    async with AsyncClient(app=app_with_nonce, base_url="http://test") as client:
        response = await client.post("/test", headers={"X-Request-Nonce": "new123"})
        
    assert response.status_code == 200
    assert response.headers["X-Request-Nonce"] == "new123"
