import pytest
from unittest.mock import patch
from app.models.user_model import User
from jose import jwt
from datetime import datetime, timezone, timedelta

@pytest.mark.anyio
async def test_logout_success(client):
    mock_user = User(id=1, email="test@example.com")
    
    from app.api.depedencies import get_current_user, security
    from app.main import app
    from fastapi.security import HTTPAuthorizationCredentials
    
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, 
        "secret", 
        algorithm="HS256"
    )
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[security] = lambda: HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    
    with patch("app.api.auth.views.settings.JWT_SECRET", "secret"), \
         patch("app.api.auth.views.settings.ALGORITHM", "HS256"), \
         patch("app.api.auth.views.redis_client.setex") as mock_setex:
        
        response = await client.post("/api/v1/auth/logout")
        
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    assert mock_setex.called
    
@pytest.mark.anyio
async def test_logout_invalid_payload(client):
    mock_user = User(id=1, email="test@example.com")
    
    from app.api.depedencies import get_current_user, security
    from app.main import app
    from fastapi.security import HTTPAuthorizationCredentials
    
    token = jwt.encode(
        {"sub": "1"}, 
        "secret", 
        algorithm="HS256"
    )
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[security] = lambda: HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    
    with patch("app.api.auth.views.settings.JWT_SECRET", "secret"), \
         patch("app.api.auth.views.settings.ALGORITHM", "HS256"):
        
        response = await client.post("/api/v1/auth/logout")
        
    app.dependency_overrides.clear()
    
    assert response.status_code == 400
