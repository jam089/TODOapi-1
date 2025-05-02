from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import TokenInfoSchm, UserSchmExtended
from api.auth.utils import create_access_token, create_refresh_token
from core.models import db_helper, User
from .validation import (
    get_auth_user_from_db,
    get_currant_auth_user_for_refresh,
)

router = APIRouter()


@router.post("/login/", response_model=TokenInfoSchm)
async def auth_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
):

    user = await get_auth_user_from_db(
        session,
        form_data.username,
        form_data.password,
    )
    access_token = create_access_token(user, response=response)
    refresh_token = create_refresh_token(user, response=response)
    return TokenInfoSchm(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh/",
    response_model=TokenInfoSchm,
    response_model_exclude_none=True,
)
async def auth_user(
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user_for_refresh)],
    response: Response,
):
    access_token = create_access_token(User(**user.model_dump()), response=response)
    return TokenInfoSchm(
        access_token=access_token,
    )
