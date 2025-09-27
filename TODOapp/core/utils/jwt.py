from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.api.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.api.auth_jwt.algorithm,
    expire_minutes: int = settings.api.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_payload = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_payload.update(
        iat=now,
        exp=expire,
    )
    token = jwt.encode(payload=to_payload, key=private_key, algorithm=algorithm)
    return token


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.api.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.api.auth_jwt.algorithm,
) -> dict[str, Any]:
    decoded: dict[str, Any] = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
    password: str | bytes,
) -> bytes:
    if isinstance(password, str):
        password = password.encode()
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)
