import pytest
from unittest.mock import patch

@pytest.mark.anyio
async def test_google_login_success(client):
    with patch("app.api.auth.views.AuthUseCase.get_google_auth_url", return_value="http://mock-auth-url.com"):
        response = await client.get("/api/v1/auth/google/login")
        
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["auth_url"] == "http://mock-auth-url.com"
    
    cookies = response.cookies
    assert "oauth_state" in cookies
    assert "oauth_nonce" in cookies
