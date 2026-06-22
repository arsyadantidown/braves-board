import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.anyio
async def test_google_callback_success(client):
    mock_result = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token"
    }
    
    with patch("app.api.auth.views.AuthUseCase.handle_google_callback", return_value=mock_result), \
         patch("app.api.auth.views.UserRepository", return_value=MagicMock()):
        
        client.cookies.set("oauth_state", "valid_state")
        client.cookies.set("oauth_nonce", "valid_nonce")
        
        response = await client.get(
            "/api/v1/auth/google/callback",
            params={"code": "valid_code", "state": "valid_state"},
            follow_redirects=False
        )
        
    assert response.status_code in [302, 303, 307]
    assert response.headers["location"].endswith("/dashboard")
    
    cookies = response.cookies
    assert "access_token" in cookies
    assert cookies["access_token"] == "mock_access_token"
    assert "refresh_token" in cookies
    assert cookies["refresh_token"] == "mock_refresh_token"

@pytest.mark.anyio
async def test_google_callback_missing_code(client):
    response = await client.get("/api/v1/auth/google/callback", follow_redirects=False)
    assert response.status_code in [302, 303, 307]
    assert "error=invalid_request" in response.headers["location"]

@pytest.mark.anyio
async def test_google_callback_invalid_state(client):
    client.cookies.set("oauth_state", "some_state")
    response = await client.get(
        "/api/v1/auth/google/callback", 
        params={"code": "valid_code", "state": "different_state"},
        follow_redirects=False
    )
    assert response.status_code in [302, 303, 307]
    assert "error=csrf_validation_failed" in response.headers["location"]

@pytest.mark.anyio
async def test_google_callback_missing_nonce(client):
    client.cookies.set("oauth_state", "valid_state")
    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"code": "valid_code", "state": "valid_state"},
        follow_redirects=False
    )
    assert response.status_code in [302, 303, 307]
    assert "error=nonce_validation_failed" in response.headers["location"]
    
@pytest.mark.anyio
async def test_google_callback_use_case_exception(client):
    with patch("app.api.auth.views.AuthUseCase.handle_google_callback", side_effect=Exception("Auth failed")), \
         patch("app.api.auth.views.UserRepository", return_value=MagicMock()):
        
        client.cookies.set("oauth_state", "valid_state")
        client.cookies.set("oauth_nonce", "valid_nonce")
        
        response = await client.get(
            "/api/v1/auth/google/callback",
            params={"code": "valid_code", "state": "valid_state"},
            follow_redirects=False
        )
        
    assert response.status_code in [302, 303, 307]
    assert "error=google_auth_failed" in response.headers["location"]
