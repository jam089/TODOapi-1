from datetime import timedelta, datetime, UTC
import uuid

from core.config import settings
from core.utils.jwt import encode_jwt
from core.models import User

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_token(
    token_type: str,
    payload: dict,
    expire_minutes: int = settings.api.auth_jwt.access_token_expire_minutes,
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


def create_access_token(user: User) -> str:
    jwt_payload = {
        "iss": "TODOapi-1@jam089.com",
        "sub": user.id,
        "username": user.username,
        "jti": str(uuid.uuid4()),
        "name": user.name,
        "logged_in_at": datetime.now(UTC).timestamp(),
    }
    return create_token(
        token_type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=settings.api.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: User):
    jwt_payload = {
        "sub": user.id,
    }
    return create_token(
        token_type=REFRESH_TOKEN_TYPE,
        payload=jwt_payload,
        expire_timedelta=timedelta(
            days=settings.api.auth_jwt.refresh_token_expire_days,
        ),
    )
