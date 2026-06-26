import time
import logging
import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger("app.http")


class DbLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs HTTP request/response data and application-level
    errors to TimescaleDB via the TimescaleLogHandler.

    Captures:
    - HTTP log: method, path, status_code, duration, IP, user_agent, request_id
    - Application log: unhandled exceptions with traceback
    """

    # Paths to exclude from logging (health checks, metrics, etc.)
    EXCLUDED_PATHS = {"/api/v1/health", "/metrics", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.time()
        request_id = getattr(request.state, "request_id", None)
        client_ip = request.client.host if request.client else "127.0.0.1"
        user_agent = request.headers.get("user-agent", "")

        # Try to get user_id from request state (set by auth dependency)
        user_id = None

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Try to extract user_id from request state after processing
            user_id = getattr(request.state, "user_id", None)

            # Determine log level based on status code
            if response.status_code >= 500:
                level = logging.ERROR
            elif response.status_code >= 400:
                level = logging.WARNING
            else:
                level = logging.INFO

            # Create log record for HTTP request
            record = logger.makeRecord(
                name="app.http",
                level=level,
                fn="",
                lno=0,
                msg=f"{request.method} {request.url.path} {response.status_code} {duration_ms:.2f}ms",
                args=(),
                exc_info=None,
            )
            record.log_type = "http"
            record.log_extra = {
                "user_id": user_id,
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "ip_address": client_ip,
                "user_agent": user_agent,
            }
            logger.handle(record)

            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            # Log the unhandled exception as application-level error
            record = logger.makeRecord(
                name="app.error",
                level=logging.ERROR,
                fn="",
                lno=0,
                msg=f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
                args=(),
                exc_info=None,
            )
            record.log_type = "application"
            record.log_extra = {
                "user_id": user_id,
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": round(duration_ms, 2),
                "ip_address": client_ip,
                "user_agent": user_agent,
                "traceback": traceback.format_exc(),
            }
            logger.handle(record)

            raise


def setup_db_logging(app):
    """Add the database logging middleware to the FastAPI app."""
    app.add_middleware(DbLoggingMiddleware)
