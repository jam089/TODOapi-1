from datetime import datetime, timedelta, UTC

import jwt
import bcrypt

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_payload = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now - expire_timedelta
    else:
        expire = now - timedelta(minutes=expire_minutes)
    to_payload.update(
        iat=now,
        exp=expire,
    )
    token = jwt.encode(payload=to_payload, key=private_key, algorithm=algorithm)
    return token


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)
