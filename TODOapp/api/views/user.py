from typing import Sequence, Annotated, Union

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from api.schemas import UserSchm, UserSchmExtended
from core.crud import user

router = APIRouter()


@router.get("/{username}/", response_model=UserSchm)
async def get_user_by_username(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    username: str,
):
    return await user.get_user_by_username(session, username)


@router.get(
    "/",
    response_model=Union[
        UserSchmExtended,
        Sequence[UserSchmExtended],
    ],
)
async def get_all_user_and_by_id(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: Annotated[int, Path] | None = None,
):
    if id:
        return await user.get_user_by_id(session, id)

    return await user.get_all_users(session)
