import os

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.connections.redis import redis_client
from app.settings import settings

IS_TEST = os.getenv("APP_ENV", "").lower() == "test"

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_limit=50, default_window=60):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window

        self.strict_paths = {
            "/api/v1/auth": {"limit": 5, "window": 60},
            "/api/v1/tasks": {"limit": 20, "window": 60},
        }

    async def dispatch(self, request: Request, call_next):
        
        if IS_TEST:
            return await call_next(request)
        
        ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path

        limit = self.default_limit
        window = self.default_window
        rate_limit_category = "global"

        for strict_path, config in self.strict_paths.items():
            if path.startswith(strict_path):
                limit = config["limit"]
                window = config["window"]
                rate_limit_category = strict_path
                break

        key = f"rate_limit:{ip}:{rate_limit_category}"
        now_timestamp = time.time()
        member_id = f"{now_timestamp}:{uuid.uuid4().hex}"

        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, now_timestamp - window)
            pipe.zadd(key, {member_id: now_timestamp})
            pipe.zcard(key)
            pipe.expire(key, window)

            results = await pipe.execute()

        count = results[2]

        if count > limit:
            return JSONResponse(
                status_code=429,
                headers={
                    "Access-Control-Allow-Origin": settings.FRONTEND_URL,
                    "Access-Control-Allow-Credentials": "true",
                },
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED", 
                        "message": "Terlalu banyak permintaan. Silakan coba lagi nanti."
                    }
                },
            )

        return await call_next(request)

def setup_rate_limit(app):
    app.add_middleware(RateLimitMiddleware)