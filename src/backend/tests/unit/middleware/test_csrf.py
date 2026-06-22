import pytest
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient
from unittest.mock import patch
from app.middleware.csrf import setup_csrf

@pytest.fixture
def app_with_csrf():
    app = FastAPI()
    setup_csrf(app)
    
    @app.post("/test")
    async def test_post():
        return {"message": "ok"}
        
    @app.get("/test")
    async def test_get():
        return {"message": "ok"}
        
    @app.post("/api/v1/auth/google/login")
    async def test_exempt():
        return {"message": "ok"}
        
    return app

@pytest.mark.anyio
async def test_csrf_exempt_path(app_with_csrf):
    async with AsyncClient(app=app_with_csrf, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/google/login")
    assert response.status_code == 200

@pytest.mark.anyio
async def test_csrf_get_ignored(app_with_csrf):
    async with AsyncClient(app=app_with_csrf, base_url="http://test") as client:
        response = await client.get("/test")
    assert response.status_code == 200

@pytest.mark.anyio
@patch("app.middleware.csrf.settings.FRONTEND_URL", "http://myfrontend.com")
async def test_csrf_valid_origin(app_with_csrf):
    async with AsyncClient(app=app_with_csrf, base_url="http://test") as client:
        response = await client.post("/test", headers={"origin": "http://myfrontend.com"})
    assert response.status_code == 200

@pytest.mark.anyio
@patch("app.middleware.csrf.settings.FRONTEND_URL", "http://myfrontend.com")
async def test_csrf_invalid_origin(app_with_csrf):
    async with AsyncClient(app=app_with_csrf, base_url="http://test") as client:
        with pytest.raises(HTTPException) as exc_info:
            await client.post("/test", headers={"origin": "http://evil.com"})
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Invalid origin"

@pytest.mark.anyio
@patch("app.middleware.csrf.settings.FRONTEND_URL", "http://myfrontend.com")
@patch("app.middleware.csrf.settings.APP_ENV", "production")
async def test_csrf_missing_headers_production(app_with_csrf):
    async with AsyncClient(app=app_with_csrf, base_url="http://test") as client:
        with pytest.raises(HTTPException) as exc_info:
            await client.post("/test")
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Missing origin or referer headers"
