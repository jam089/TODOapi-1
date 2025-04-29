from typing import Sequence, Annotated, Union

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.validation import get_currant_auth_user, get_currant_auth_user_with_admin
from api.schemas import UserSchm, UserSchmExtended, CreateUserSchm, UpdateUserSchm
from api import deps
from api.schemas.user import UserPassChangeSchm, UserRoleChangeSchm
from api.http_exceptions import (
    rendering_exception_with_param,
    username_already_exist_exc_templ,
    role_not_exist_exc_templ,
    user_id_exc_templ,
    no_priv_except,
    user_exception_templ,
)
from core.config import settings
from core.models import db_helper
from core.models import User as UserModel
from core.crud import user

router = APIRouter()


@router.get(
    "/profile/",
    response_model=UserSchmExtended,
    summary="Get Self Profile",
    description="Authentication is required",
)
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
    raise rendering_exception_with_param(
        user_exception_templ,
        username,
    )


@router.get(
    "/",
    response_model=Union[
        UserSchmExtended,
        Sequence[UserSchm],
    ],
    summary="Get All User Or Get User By Id",
    description=f"Authentication is required for request for all users (without query id) or<br>"
    f"Authentication and {settings.roles.admin} role is required for specific user",
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
            raise no_priv_except
        user_by_id: UpdateUserSchm | None = await user.get_user_by_id(session, id)
        if user_by_id:
            return user_by_id
        raise rendering_exception_with_param(user_id_exc_templ, str(id))

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
    raise rendering_exception_with_param(
        username_already_exist_exc_templ,
        user_to_create.username,
    )


@router.patch(
    "/change_password/",
    response_model=UserSchmExtended,
    summary="Change Self Password",
    description="Authentication is required",
)
async def change_your_password(
    new_password: UserPassChangeSchm,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user),
    ],
):
    user_to_update = await user.get_user_by_id(session, current_user.id)
    return await user.update_password(
        session=session,
        user_to_update=user_to_update,
        password=new_password.password,
    )


@router.patch(
    "/{user_id}/role/",
    response_model=UserSchmExtended,
    description=f"Authentication and {settings.roles.admin} role is required",
)
async def change_role(
    new_role: UserRoleChangeSchm,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_to_update: Annotated[UserModel, Depends(deps.get_user)],
    _current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user_with_admin),
    ],
):
    role_dict = settings.roles.model_dump()
    if new_role.role not in role_dict.values():
        raise rendering_exception_with_param(
            role_not_exist_exc_templ,
            new_role.role,
        )

    return await user.update_role(session, user_to_update, new_role.role)


@router.patch(
    "/{user_id}/",
    response_model=UserSchmExtended,
    description=f"Authentication and {settings.roles.admin} role is required",
)
async def update_user(
    user_input: UpdateUserSchm,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_to_update: Annotated[UserModel, Depends(deps.get_user)],
    _current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user_with_admin),
    ],
):
    if not await user.get_user_by_username(session, user_input.username):
        return await user.update_user(session, user_to_update, user_input)
    raise rendering_exception_with_param(
        username_already_exist_exc_templ,
        user_input.username,
    )


@router.patch(
    "/",
    response_model=UserSchmExtended,
    description="Authentication is required",
)
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
    raise rendering_exception_with_param(
        username_already_exist_exc_templ,
        user_input.username,
    )


@router.delete(
    "/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    description=f"Authentication and {settings.roles.admin} role is required",
)
async def delete_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_to_delete: Annotated[UserModel, Depends(deps.get_user)],
    _current_user: Annotated[
        UserSchmExtended,
        Depends(get_currant_auth_user_with_admin),
    ],
) -> None:
    await user.delete_user(session, user_to_delete)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Authentication is required",
)
async def delete_yourself(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
) -> None:
    user_in_db: UserModel = await user.get_user_by_id(session, current_user.id)
    await user.delete_user(session, user_in_db)
