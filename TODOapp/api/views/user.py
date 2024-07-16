from typing import Sequence, Annotated, Union

from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import UserSchm, UserSchmExtended, CreateUserSchm, UpdateUserSchm
from api import deps
from core.models import db_helper
from core.models import User as UserModel
from core.crud import user

router = APIRouter()


@router.get("/{username}/", response_model=UserSchm)
async def get_user_by_username(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    username: str,
):
    user_by_username: UserModel | None = await user.get_user_by_username(
        session, username
    )
    if user_by_username:
        return user_by_username
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"user {username!r} not found",
    )


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
        user_by_id: UpdateUserSchm | None = await user.get_user_by_id(session, id)
        if user_by_id:
            return user_by_id
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id=[{int(id)}] not found",
        )

    return await user.get_all_users(session)


@router.post(
    "/",
    response_model=UserSchm,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_to_create: CreateUserSchm,
):
    if not await user.get_user_by_username(session, user_to_create.username):
        return await user.create_user(session, user_to_create)
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{user_to_create.username} already exist",
    )


@router.patch("/{user_id}/", response_model=UserSchm)
async def update_user(
    user_input: UpdateUserSchm,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_to_update: Annotated[UserModel, Depends(deps.get_user)],
):
    if not await user.get_user_by_username(session, user_input.username):
        return await user.update_user(session, user_to_update, user_input)
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{user_input.username} already exist",
    )


@router.delete(
    "/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_to_delete: Annotated[UserModel, Depends(deps.get_user)],
) -> None:
    await user.delete_user(session, user_to_delete)
