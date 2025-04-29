from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.validation import get_currant_auth_user_with_admin, get_currant_auth_user
from api.schemas import (
    TaskSchm,
    UserSchmExtended,
    CreateTaskSchm,
    UpdateTaskSchm,
    SearchTaskSchm,
)
from api import deps
from api.http_exceptions import (
    rendering_exception_with_param,
    no_priv_except,
    task_not_exist_except,
    status_exception_templ,
)
from core.config import settings
from core.models import db_helper, Task
from core.models.user import User as UserModel
from core.crud import task as crud

router = APIRouter()


@router.get(
    "/all/",
    response_model=Sequence[TaskSchm],
    description=f"Authentication and {settings.roles.admin} role is required",
)
async def get_all_tasks(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    admin: Annotated[UserSchmExtended, Depends(get_currant_auth_user_with_admin)],
):
    return await crud.get_all_tasks(session)


@router.get(
    "/{task_id}/",
    response_model=TaskSchm,
    description=f"Authentication and {settings.roles.admin} role is required",
)
async def get_task_by_task_id(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_id: int,
    admin: Annotated[UserSchmExtended, Depends(get_currant_auth_user_with_admin)],
):
    return await crud.get_task_by_id(session, task_id)


@router.get(
    "/user-id={user_id}/",
    response_model=Sequence[TaskSchm],
    description=f"Authentication and {settings.roles.admin} role is required",
)
async def get_task_by_user_id(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[UserModel, Depends(deps.get_user)],
    admin: Annotated[UserSchmExtended, Depends(get_currant_auth_user_with_admin)],
):
    return await crud.get_user_all_tasks(session, UserSchmExtended.model_validate(user))


@router.get(
    "/search/",
    response_model=Sequence[TaskSchm],
    description="Authentication is required",
)
async def search_task_by_parameters(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    search_task: Annotated[SearchTaskSchm, Depends()],
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    if (
        search_task.status
        and search_task.status not in settings.tstat.model_dump().values()
    ):
        raise rendering_exception_with_param(
            status_exception_templ,
            search_task.status,
        )
    return await crud.get_tasks_by_some_statement(session, search_task)


@router.get(
    "/",
    response_model=Sequence[TaskSchm],
    description="Authentication is required",
)
async def get_user_all_tasks(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    return await crud.get_user_all_tasks(session, user)


@router.post(
    "/",
    response_model=TaskSchm,
    status_code=status.HTTP_201_CREATED,
    description="Authentication is required",
)
async def create_task(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_input: CreateTaskSchm,
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    return await crud.create_task(session, task_input, user)


@router.patch(
    "/{task_id}/change_owner/",
    response_model=TaskSchm,
    description=f"Authentication is required for user`s tasks and"
    f" {settings.roles.admin} role is required for other tasks",
)
async def change_task_owner(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_id: int,
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
    new_user: Annotated[UserModel, Depends(deps.get_user)],
):
    task_to_update: Task = await crud.get_task_by_id(session, task_id)
    if task_to_update is None:
        raise task_not_exist_except
    if task_to_update.user_id == user.id or user.role == settings.roles.admin:
        return await crud.change_task_user_by_user(
            session=session,
            task_to_update=task_to_update,
            new_user=new_user,
        )
    raise no_priv_except


@router.patch(
    "/{task_id}/",
    response_model=TaskSchm,
    description=f"Authentication is required for user`s tasks and"
    f" {settings.roles.admin} role is required for other tasks",
)
async def update_task(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_input: UpdateTaskSchm,
    task_id: int,
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    if (
        task_input.status
        and task_input.status not in settings.tstat.model_dump().values()
    ):
        raise rendering_exception_with_param(
            status_exception_templ,
            task_input.status,
        )
    task_to_update: Task = await crud.get_task_by_id(session, task_id)
    if task_to_update is None:
        raise task_not_exist_except
    if task_to_update.user_id == user.id or user.role == settings.roles.admin:
        return await crud.update_task(session, task_to_update, task_input)
    raise no_priv_except


@router.delete(
    "/{task_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    description=f"Authentication is required for user`s tasks and"
    f" {settings.roles.admin} role is required for other tasks",
)
async def delete_task(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_id: int,
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
) -> None:
    task_to_delete: Task = await crud.get_task_by_id(session, task_id)
    if task_to_delete is None:
        raise task_not_exist_except
    if task_to_delete.user_id == user.id or user.role == settings.roles.admin:
        await crud.delete_task(session, task_to_delete)
        return None
    raise no_priv_except
