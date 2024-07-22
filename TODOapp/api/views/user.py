from typing import Sequence, Annotated, Union

from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.validation import get_currant_auth_user, get_currant_auth_user_with_admin
from api.schemas import UserSchm, UserSchmExtended, CreateUserSchm, UpdateUserSchm
from api import deps
from core.config import settings
from core.models import db_helper
from core.models import User as UserModel
from core.crud import user

router = APIRouter()


@router.get("/profile/", response_model=UserSchmExtended)
async def get_profile(
    current_user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    return current_user


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
        Sequence[UserSchm],
    ],
)
async def get_all_user_and_by_id(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user),
    ],
    id: Annotated[int, Path] | None = None,
):
    if id:
        if current_user.role != settings.roles.admin:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="not enough privileges",
            )
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
    current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user_with_admin),
    ],
):
    if not await user.get_user_by_username(session, user_input.username):
        return await user.update_user(session, user_to_update, user_input)
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{user_input.username} already exist",
    )


@router.patch("/", response_model=UserSchmExtended)
async def update_yourself(
    user_input: UpdateUserSchm,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user),
    ],
):
    user_to_update = await user.get_user_by_id(session, current_user.id)
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
    current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user_with_admin),
    ],
) -> None:
    await user.delete_user(session, user_to_delete)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_yourself(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
) -> None:
    user_in_db: UserModel = await user.get_user_by_id(session, current_user.id)
    await user.delete_user(session, user_in_db)
