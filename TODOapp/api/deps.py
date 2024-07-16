from typing import Annotated

from fastapi import Depends, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"user with id=[{int(user_id)}] not found",
    )
