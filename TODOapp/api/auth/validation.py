from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from .utils import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from ..schemas import UserSchmExtended
from core.crud.user import get_user_by_id, get_user_by_username
from core.utils.jwt import decode_jwt, check_password

tokenUrl = f"{settings.api.prefix}{settings.api.auth_jwt.prefix}/login/"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl)

token_invalid_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
)

unauth_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid login or password",
)


def validate_token_type(
    payload: dict,
    token_type: str,
) -> bool:
    if payload.get(TOKEN_TYPE_FIELD) == token_type:
        return True
    raise token_invalid_exc


async def get_user_from_payload(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    payload: dict,
) -> UserSchmExtended:
    user_id: int | None = payload.get("sub")
    if user := await get_user_by_id(session, user_id):
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user is inactive",
            )
        return UserSchmExtended.model_validate(user)
    raise token_invalid_exc


def get_currant_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        raise token_invalid_exc
    return payload


def get_auth_user_from_token_of_type(token_type: str):
    async def get_auth_user_from_token(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        payload: Annotated[dict, Depends(get_currant_token_payload)],
    ) -> UserSchmExtended:
        validate_token_type(payload, token_type)
        return await get_user_from_payload(session, payload)

    return get_auth_user_from_token


get_currant_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TYPE)
get_currant_auth_user_for_refresh = get_auth_user_from_token_of_type(REFRESH_TOKEN_TYPE)


async def get_auth_user_from_db(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    username: str,
    password: str,
) -> User:
    user: User = await get_user_by_username(
        session=session,
        username=username,
    )

    if not user:
        raise unauth_exc

    if not check_password(
        password=password,
        hashed_password=user.password.encode(),
    ):
        raise unauth_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user is inactive",
        )

    return user
