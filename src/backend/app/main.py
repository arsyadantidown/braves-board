import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.settings import settings
from app.api.main import api_router
from app.observability.middleware import setup_prometheus
from app.observability.metrics import metrics_endpoint
from app.api.health.views import router as health_router

from app.middleware.cors import setup_cors
from app.middleware.request_id import setup_request_id
from app.middleware.access_log import setup_access_log
from app.middleware.rate_limit import setup_rate_limit
from app.middleware.security_headers import setup_security_headers
from app.middleware.nonce import setup_nonce
from app.middleware.csrf import setup_csrf
from app.middleware.db_logging import setup_db_logging
from app.api.exceptions.setup_exceptions import setup_exception_handlers
from app.lib.logging.timescale_handler import setup_log_handler, shutdown_log_handler

IS_TEST = (settings.APP_ENV or "").lower() == "test"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize TimescaleDB log handler
    if not IS_TEST:
        await setup_log_handler()

    yield

    # Shutdown: flush and close log handler
    if not IS_TEST:
        await shutdown_log_handler()


if settings.APP_ENV in ["production", "staging"]:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan)


metrics_security = HTTPBearer()

async def verify_metrics_token(credentials: HTTPAuthorizationCredentials = Depends(metrics_security)):
    if credentials.credentials != settings.METRICS_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid metrics token"
        )

setup_security_headers(app)

if not IS_TEST:
    setup_nonce(app)
    setup_csrf(app)
    setup_rate_limit(app)

setup_access_log(app)
setup_db_logging(app)
setup_request_id(app)
setup_cors(app)

setup_exception_handlers(app)

setup_prometheus(app)

app.add_api_route(
    "/metrics",
    metrics_endpoint,
    methods=["GET"],
    dependencies=[Depends(verify_metrics_token)]
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(api_router)