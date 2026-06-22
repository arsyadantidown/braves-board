import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from app.connections.redis import redis_client
from app.main import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(autouse=True)
def mock_redis():
    # Keep reference to original methods
    orig_pipeline = redis_client.pipeline
    orig_exists = redis_client.exists
    orig_setex = redis_client.setex
    
    # Mock them
    mock_pipe = MagicMock()
    mock_pipe.execute = AsyncMock(return_value=[0, 0, 1])
    mock_pipe.zremrangebyscore = MagicMock()
    mock_pipe.zadd = MagicMock()
    mock_pipe.zcard = MagicMock()
    mock_pipe.expire = MagicMock()
    mock_pipe.setex = MagicMock()
    mock_pipe.__aenter__ = AsyncMock(return_value=mock_pipe)
    mock_pipe.__aexit__ = AsyncMock()
    
    redis_client.pipeline = MagicMock(return_value=mock_pipe)
    redis_client.exists = AsyncMock(return_value=False)
    redis_client.setex = AsyncMock()
    
    yield
    
    # Restore
    redis_client.pipeline = orig_pipeline
    redis_client.exists = orig_exists
    redis_client.setex = orig_setex

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

