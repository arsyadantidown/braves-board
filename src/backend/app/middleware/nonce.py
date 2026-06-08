from fastapi import HTTPException, status
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
        # 1. Skip endpoint yang sudah punya mekanisme nonce sendiri (Google OAuth)
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # 2. Hanya proteksi method yang memodifikasi data (non-idempotent)
        if request.method not in PROTECTED_METHODS:
            return await call_next(request)

        # 3. Validasi keberadaan header X-Request-Nonce
        nonce = request.headers.get("X-Request-Nonce")
        if not nonce:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Request-Nonce header is required for non-idempotent requests",
            )

        # 4. Cek apakah nonce sudah pernah digunakan (replay detection)
        key = f"nonce:{nonce}"
        exists = await redis_client.exists(key)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Replay attack detected: duplicate nonce",
            )

        # 5. Simpan nonce ke Redis dengan TTL (gunakan pipeline agar atomic)
        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.setex(key, NONCE_TTL_SECONDS, "1")
            await pipe.execute()

        # 6. Sertakan nonce di response header untuk referensi client
        response = await call_next(request)
        response.headers["X-Request-Nonce"] = nonce
        return response


def setup_nonce(app):
    app.add_middleware(NonceMiddleware)