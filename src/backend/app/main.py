import os

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
from app.api.exceptions.setup_exceptions import setup_exception_handlers

IS_TEST = (settings.APP_ENV or "").lower() == "test"

if settings.APP_ENV in ["production", "staging"]:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
else:
    app = FastAPI()


metrics_security = HTTPBearer()

async def verify_metrics_token(credentials: HTTPAuthorizationCredentials = Depends(metrics_security)):
    if credentials.credentials != settings.METRICS_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid metrics token"
        )

setup_security_headers(app)
setup_access_log(app)
setup_request_id(app)
setup_cors(app)

if not IS_TEST:
    setup_rate_limit(app)
    setup_nonce(app)
    setup_csrf(app)

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

from fastapi.openapi.utils import get_openapi
from app.middleware.nonce import EXEMPT_PATHS, PROTECTED_METHODS

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    
    protected_methods = {m.lower() for m in PROTECTED_METHODS}
    
    for path, path_item in openapi_schema.get("paths", {}).items():
        if path in EXEMPT_PATHS:
            continue
        for method, operation in path_item.items():
            if method.lower() in protected_methods:
                if "parameters" not in operation:
                    operation["parameters"] = []
                operation["parameters"].append({
                    "name": "X-Request-Nonce",
                    "in": "header",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": "Unique nonce for replay attack protection."
                })
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi