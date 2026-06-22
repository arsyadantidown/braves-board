import pytest
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.depedencies import get_current_user
from app.models.user_model import User


# =========================
# MOCK USER
# =========================

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

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac

@pytest.fixture(autouse=True)
def mock_storage_util(monkeypatch):

    class FakeStorageUtil:

        def upload_file(self, *args, **kwargs):
            return "https://example.com/file.png"

        def generate_signed_url(self, file_url):
            return file_url

        def delete_file(self, *args, **kwargs):
            pass

    monkeypatch.setattr(
        "app.api.task_attachment.use_cases.StorageUtil",
        FakeStorageUtil
    )