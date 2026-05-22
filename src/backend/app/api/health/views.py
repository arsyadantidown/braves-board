from fastapi import APIRouter, status, Response
from sqlalchemy import text

from app.api.health.schema import HealthData, ReadinessData
from app.connections.postgres import AsyncSessionLocal
from app.connections.redis import redis_client

router = APIRouter(tags=["Health Check"])

@router.get(
    "/healthz",
    response_model=HealthData,
    status_code=status.HTTP_200_OK,
)
async def liveness_check():
    return HealthData(
        status="ok",
        message="Application is alive",
    )

@router.get(
    "/readyz",
    response_model=ReadinessData,
)
async def readiness_check(response: Response):
    db_status = "ok"
    redis_status = "ok"

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        await redis_client.ping()
    except Exception:
        redis_status = "error"

    overall_status = "ok"

    if db_status != "ok" or redis_status != "ok":
        overall_status = "error"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        response.status_code = status.HTTP_200_OK

    return ReadinessData(
        status=overall_status,
        database=db_status,
        redis=redis_status,
    )