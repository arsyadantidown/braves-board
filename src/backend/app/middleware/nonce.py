from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.connections.redis import redis_client

NONCE_TTL_SECONDS = 300  # 5 menit

EXEMPT_PATHS = {
    "/api/v1/auth/google/login",
    "/api/v1/auth/google/callback",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
}

PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class NonceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        if request.method not in PROTECTED_METHODS:
            return await call_next(request)

        nonce = request.headers.get("X-Request-Nonce")
        if not nonce:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "X-Request-Nonce header is required for non-idempotent requests"},
            )

        key = f"nonce:{nonce}"
        exists = await redis_client.exists(key)
        if exists:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Replay attack detected: duplicate nonce"},
            )

        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.setex(key, NONCE_TTL_SECONDS, "1")
            await pipe.execute()

        response = await call_next(request)
        response.headers["X-Request-Nonce"] = nonce
        return response


def setup_nonce(app):
    app.add_middleware(NonceMiddleware)