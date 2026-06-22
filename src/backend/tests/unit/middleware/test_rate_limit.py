import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.middleware.rate_limit import setup_rate_limit

@pytest.fixture
def app_with_rate_limit():
    app = FastAPI()
    setup_rate_limit(app)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}
        
    @app.get("/api/v1/auth/test")
    async def auth_test_endpoint():
        return {"message": "ok"}
        
    return app

@pytest.mark.anyio
async def test_rate_limit_pass(app_with_rate_limit):
    mock_pipeline = MagicMock()
    mock_pipeline.execute = AsyncMock(return_value=[1, 1, 1])
    mock_pipeline.__aenter__ = AsyncMock(return_value=mock_pipeline)
    mock_pipeline.__aexit__ = AsyncMock()

    with patch("app.middleware.rate_limit.redis_client.pipeline", return_value=mock_pipeline):
        async with AsyncClient(app=app_with_rate_limit, base_url="http://test") as client:
            response = await client.get("/test")
            
    assert response.status_code == 200

@pytest.mark.anyio
async def test_rate_limit_exceeded(app_with_rate_limit):
    mock_pipeline = MagicMock()
    mock_pipeline.execute = AsyncMock(return_value=[1, 1, 51]) 
    mock_pipeline.__aenter__ = AsyncMock(return_value=mock_pipeline)
    mock_pipeline.__aexit__ = AsyncMock()

    with patch("app.middleware.rate_limit.redis_client.pipeline", return_value=mock_pipeline):
        async with AsyncClient(app=app_with_rate_limit, base_url="http://test") as client:
            response = await client.get("/test")
            
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

@pytest.mark.anyio
async def test_rate_limit_strict_path_exceeded(app_with_rate_limit):
    mock_pipeline = MagicMock()
    mock_pipeline.execute = AsyncMock(return_value=[1, 1, 6]) 
    mock_pipeline.__aenter__ = AsyncMock(return_value=mock_pipeline)
    mock_pipeline.__aexit__ = AsyncMock()

    with patch("app.middleware.rate_limit.redis_client.pipeline", return_value=mock_pipeline):
        async with AsyncClient(app=app_with_rate_limit, base_url="http://test") as client:
            response = await client.get("/api/v1/auth/test")
            
    assert response.status_code == 429
