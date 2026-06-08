import httpx
import urllib.parse
import uuid
from jose import jwt, JWTError

from app.settings import settings
from app.api.auth.repository import UserRepository
from app.api.auth.schema import UserCreate
from app.lib import jwt_utils
from app.api.exceptions.auth_exceptions import (
    GoogleAuthException,
    InvalidGoogleCodeException,
    ForbiddenDomainException,
    InvalidRefreshTokenException,
)

class AuthUseCase:
    @staticmethod
    def get_google_auth_url(state: str | None = None) -> str:
        try:
            base_url = "https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile",
                "access_type": "offline",
                "prompt": "consent",
            }
            if state:
                params["state"] = state
            return f"{base_url}?{urllib.parse.urlencode(params)}"
        except Exception:
            raise GoogleAuthException()

    @staticmethod
    async def handle_google_callback(code: str, user_repo: UserRepository):
        decoded_code = urllib.parse.unquote(code)

        async with httpx.AsyncClient() as client:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": decoded_code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            res = await client.post(token_url, data=data)

            if res.status_code != 200:
                raise InvalidGoogleCodeException()

            google_tokens = res.json()
            access_token = google_tokens.get("access_token")

            user_info_res = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile = user_info_res.json()
            email = profile.get("email")

            if not email or not email.endswith("@bangunindo.com"):
                raise ForbiddenDomainException()

            user = await user_repo.get_by_google_id(profile.get("sub"))
            if not user:
                user_in = UserCreate(
                    email=email,
                    full_name=profile.get("name"),
                    picture_url=profile.get("picture"),
                    google_id=profile.get("sub"),
                )
                user = await user_repo.create(user_in)

            token_payload = {"sub": str(user.id)}
            access_token = jwt_utils.create_access_token(token_payload)
            refresh_token = jwt_utils.create_refresh_token(token_payload)

            return {
                "user": user,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }

    @staticmethod
    async def refresh_access_token(refresh_token: str, user_repo: UserRepository):
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET,
                algorithms=[settings.ALGORITHM],
            )

            user_id = payload.get("sub")
            token_type = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise InvalidRefreshTokenException()

            user_id_uuid = uuid.UUID(user_id)

        except (JWTError, ValueError):
            raise InvalidRefreshTokenException()

        user = await user_repo.get_by_id(user_id_uuid)
        if not user:
            raise InvalidRefreshTokenException()

        token_payload = {"sub": str(user.id)}
        new_access_token = jwt_utils.create_access_token(token_payload)

        return {
            "access_token": new_access_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }