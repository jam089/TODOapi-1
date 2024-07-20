from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import TokenInfoSchm
from api.auth.utils import create_access_token, create_refresh_token
from core.models import db_helper
from .validation import (
    get_auth_user_from_db,
)

router = APIRouter()


@router.post("/login/", response_model=TokenInfoSchm)
async def auth_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):

    user = await get_auth_user_from_db(
        session,
        form_data.username,
        form_data.password,
    )
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfoSchm(
        access_token=access_token,
        refresh_token=refresh_token,
    )
