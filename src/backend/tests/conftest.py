import pytest
import uuid
import asyncio

from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from app.connections.redis import redis_client
from app.main import app
from app.api.depedencies import get_current_user
from app.models.user_model import User

# Mock User
@pytest.fixture
def mock_user():
    return User(
        id=uuid.uuid4(),
        email="test@test.com"
    )


@pytest.fixture(autouse=True)
def reset_event_loop():
    yield
    asyncio.set_event_loop(asyncio.new_event_loop())

@pytest.fixture(autouse=True)
def override_auth(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def disable_redis(monkeypatch):
    import app.connections.redis as redis_module

    class FakeRedis:
        async def exists(self, *args, **kwargs):
            return 0

        async def ping(self):
            return True

        async def close(self):
            pass

    monkeypatch.setattr(redis_module, "redis_client", FakeRedis())

@pytest.fixture
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
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac

