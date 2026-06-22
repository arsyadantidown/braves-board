import pytest
import uuid
from datetime import datetime, timezone
from app.models.user_model import User

@pytest.mark.anyio
async def test_get_current_user_profile_success(client):
    user_id = uuid.uuid4()
    mock_user = User(
        id=user_id,
        email="test@example.com",
        full_name="Test User",
        picture_url="http://example.com/pic.jpg",
        created_at=datetime.now(timezone.utc)
    )
    
    from app.api.depedencies import get_current_user
    from app.main import app
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    response = await client.get("/api/v1/auth/me")
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["id"] == str(user_id)
    assert data["data"]["full_name"] == "Test User"

