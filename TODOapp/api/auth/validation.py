from typing import Annotated

from fastapi import Depends
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from .utils import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    get_token_of_type,
)
from ..schemas import UserSchmExtended
from ..http_exceptions import (
    token_invalid_exc,
    unauth_exc,
    no_priv_except,
    inactive_user_exception,
)
from core.crud.user import get_user_by_id, get_user_by_username
from core.utils.jwt import decode_jwt, check_password


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
            raise inactive_user_exception
        return UserSchmExtended.model_validate(user)
    raise token_invalid_exc


def get_currant_token_payload_of_token_type(
    token_type: str,
):
    def get_currant_token_payload(
        token: Annotated[str, Depends(get_token_of_type(token_type=token_type))],
    ) -> dict:
        try:
            payload = decode_jwt(token)
        except InvalidTokenError:
            raise token_invalid_exc
        return payload

    return get_currant_token_payload


def get_auth_user_from_token_of_type(
    token_type: str,
    user_role_to_check: str | None = None,
):
    async def get_auth_user_from_token(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        payload: Annotated[
            dict,
            Depends(get_currant_token_payload_of_token_type(token_type=token_type)),
        ],
    ) -> UserSchmExtended:
        validate_token_type(payload, token_type)
        if user_role_to_check is not None:
            if payload.get("role") != user_role_to_check:
                raise no_priv_except
        return await get_user_from_payload(session, payload)

    return get_auth_user_from_token


get_currant_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TYPE)
get_currant_auth_user_for_refresh = get_auth_user_from_token_of_type(REFRESH_TOKEN_TYPE)

get_currant_auth_user_with_admin = get_auth_user_from_token_of_type(
    token_type=ACCESS_TOKEN_TYPE,
    user_role_to_check=settings.roles.admin,
)


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
        raise inactive_user_exception

    return user
