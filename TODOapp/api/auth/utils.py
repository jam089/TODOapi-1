from datetime import timedelta, datetime, UTC
import uuid

from fastapi import Request, Response, Depends
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from core.utils.jwt import encode_jwt
from core.models import User

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access_token"
REFRESH_TOKEN_TYPE = "refresh_token"

TOKEN_URL = f"{settings.api.prefix}{settings.api.auth_jwt.prefix}/login/"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=TOKEN_URL,
    auto_error=False,
)


def create_token(
    token_type: str,
    payload: dict,
    expire_minutes: int = settings.api.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
    response: Response | None = None,
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: token_type,
    }
    jwt_payload.update(payload)
    token = encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )
    if response is not None:
        response.set_cookie(
            key=token_type,
            value=token,
            path=settings.api.auth_jwt.cookies.path,
            httponly=settings.api.auth_jwt.cookies.http_only,
            secure=settings.api.auth_jwt.cookies.secure,
            samesite=settings.api.auth_jwt.cookies.samesite,
        )
    return token


def create_access_token(user: User, response: Response | None = None) -> str:
    jwt_payload = {
        "iss": "TODOapi-1@jam089.com",
        "sub": user.id,
        "username": user.username,
        "jti": str(uuid.uuid4()),
        "name": user.name,
        "logged_in_at": datetime.now(UTC).timestamp(),
        "role": user.role,
    }
    return create_token(
        token_type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=settings.api.auth_jwt.access_token_expire_minutes,
        response=response,
    )


def create_refresh_token(user: User, response: Response | None = None):
    jwt_payload = {
        "sub": user.id,
    }
    return create_token(
        token_type=REFRESH_TOKEN_TYPE,
        payload=jwt_payload,
        expire_timedelta=timedelta(
            days=settings.api.auth_jwt.refresh_token_expire_days,
        ),
        response=response,
    )


def get_token_of_type(token_type: str):
    def get_token(
        request: Request,
        token: str | None = Depends(oauth2_scheme),
    ):
        if not token:
            token = request.cookies.get(token_type)
        return token

    return get_token
