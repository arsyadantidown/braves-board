import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.anyio
async def test_refresh_token_success(client):
    mock_result = {
        "access_token": "new_access_token",
        "expires_in": 3600
    }
    
    with patch("app.api.auth.views.AuthUseCase.refresh_access_token", return_value=mock_result), \
         patch("app.api.auth.views.UserRepository", return_value=MagicMock()):
        
        client.cookies.set("refresh_token", "valid_refresh_token")
        
        response = await client.post("/api/v1/auth/refresh")
        
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["access_token"] == "new_access_token"
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["expires_in"] == 3600

@pytest.mark.anyio
async def test_refresh_token_missing_cookie(client):
    response = await client.post("/api/v1/auth/refresh")
    
    assert response.status_code != 200 
