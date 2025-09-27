from typing import Annotated

from core.crud import task as task_crud
from core.crud import user as user_crud
from core.models import Task as TaskModel
from core.models import User as UserModel
from core.models import db_helper
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from .http_exceptions import (
    rendering_exception_with_param,
    task_id_exc_templ,
    user_id_exc_templ,
)


async def get_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_id: Annotated[int, Path],
) -> UserModel:
    user = await user_crud.get_user_by_id(session, user_id)
    if user:
        return user

    raise rendering_exception_with_param(user_id_exc_templ, str(user_id))


async def get_task(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_id: Annotated[int, Path],
) -> TaskModel:
    task = await task_crud.get_task_by_id(session, task_id)
    if task:
        return task

    raise rendering_exception_with_param(task_id_exc_templ, str(task_id))
