from datetime import timedelta, datetime, UTC

from core.config import settings
from core.utils.jwt import encode_jwt
from api.schemas.user import UserSchm

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_token(
    token_type: str,
    payload: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: token_type,
    }
    jwt_payload.update(payload)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: UserSchm):
    jwt_payload = {
        "sub": user.id,
        "username": user.username,
        "name": user.name,
        "logged_in_at": datetime.now(UTC)
    }
    return create_token(
        token_type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )
