from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, Cookie, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from fastapi.responses import RedirectResponse

from app.settings import settings
from app.connections.postgres import get_db
from app.connections.redis import redis_client
from app.api.auth.repository import UserRepository
from app.api.auth.schema import (
    AuthUrlData,
    CurrentUserData,
    LogoutData,
    AccessTokenData
)
from app.api.auth.use_cases import AuthUseCase
from app.api.depedencies import get_current_user, security
from app.models.user_model import User
from app.api.exceptions.auth_exceptions import (
    InvalidRefreshTokenException, 
    MissingRefreshTokenException,
    LogoutSuccessMessage
)
from app.api.standard_response import StandardResponse, success_response

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.get("/google/login", response_model=StandardResponse[AuthUrlData])
async def google_login(state: str | None = Query(default=None)):
    auth_url = AuthUseCase.get_google_auth_url(state)
    return success_response(AuthUrlData(auth_url=auth_url))

@router.get("/google/callback")
async def google_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not code or not code.strip():
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/?error=invalid_request"
        )

    user_repo = UserRepository(db)

    try:
        result = await AuthUseCase.handle_google_callback(code, user_repo)

        redirect_url = f"{settings.FRONTEND_URL}/dashboard?access_token={result['access_token']}"
        if state:
            redirect_url += f"&state={state}"

        redirect_response = RedirectResponse(url=redirect_url)

        redirect_response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
            max_age=604800,
        )

        return redirect_response

    except Exception:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/?error=google_auth_failed"
        )

@router.get("/me", response_model=StandardResponse[CurrentUserData])
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return success_response(CurrentUserData(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        picture_url=current_user.picture_url,
        created_at=current_user.created_at,
    ))

@router.post("/refresh", response_model=StandardResponse[AccessTokenData])
async def refresh_token(
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise MissingRefreshTokenException()

    user_repo = UserRepository(db)
    result = await AuthUseCase.refresh_access_token(refresh_token, user_repo)

    return success_response(AccessTokenData(
        access_token=result["access_token"],
        token_type="bearer",
        expires_in=result["expires_in"],
    ))

@router.post("/logout", response_model=StandardResponse[LogoutData])
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": False},
    )

    exp_timestamp = payload.get("exp")
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    ttl = exp_timestamp - now_timestamp 

    if ttl > 0:
        await redis_client.setex(f"blacklist:{token}", ttl, "true")

    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=False,
        httponly=True,
        samesite="lax",
    )

    return success_response(LogoutData(message=LogoutSuccessMessage.MESSAGE))