from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from .http_exceptions import rendering_exception_with_param, user_id_exc_templ
from core.models import db_helper
from core.models import User as UserModel
from core.crud import user


async def get_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_id: Annotated[int, Path],
) -> UserModel:
    user_to_update = await user.get_user_by_id(session, user_id)
    if user_to_update:
        return user_to_update

    raise rendering_exception_with_param(user_id_exc_templ, str(user_id))
