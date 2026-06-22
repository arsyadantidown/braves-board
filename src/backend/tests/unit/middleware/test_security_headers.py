import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from app.middleware.security_headers import setup_security_headers
from unittest.mock import patch

@pytest.fixture
def app_with_security_headers():
    app = FastAPI()
    setup_security_headers(app)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}
    return app

@pytest.mark.anyio
async def test_security_headers_applied(app_with_security_headers):
    async with AsyncClient(app=app_with_security_headers, base_url="http://test") as client:
        response = await client.get("/test")
        
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]

@pytest.mark.anyio
@patch("app.middleware.security_headers.settings.APP_ENV", "production")
async def test_security_headers_production(app_with_security_headers):
    async with AsyncClient(app=app_with_security_headers, base_url="http://test") as client:
        response = await client.get("/test")
        
    assert response.status_code == 200
    assert "Strict-Transport-Security" in response.headers
