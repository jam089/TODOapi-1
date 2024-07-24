from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.validation import get_currant_auth_user_with_admin, get_currant_auth_user
from api.schemas import TaskSchm, UserSchmExtended, CreateTaskSchm, UpdateTaskSchm
from api import deps
from core.config import settings
from core.models import db_helper, Task
from core.models.user import User as UserModel
from core.crud import task as crud

router = APIRouter()


@router.get("/all-tasks/", response_model=Sequence[TaskSchm])
async def get_all_tasks(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    admin: Annotated[UserSchmExtended, Depends(get_currant_auth_user_with_admin)],
):
    return await crud.get_all_tasks(session)


@router.get("/task-id={task_id}", response_model=TaskSchm)
async def get_task_by_task_id(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_id: int,
    admin: Annotated[UserSchmExtended, Depends(get_currant_auth_user_with_admin)],
):
    return await crud.get_task_by_id(session, task_id)


@router.get("/user-id={user_id}", response_model=Sequence[TaskSchm])
async def get_task_by_user_id(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[UserModel, Depends(deps.get_user)],
    admin: Annotated[UserSchmExtended, Depends(get_currant_auth_user_with_admin)],
):
    return await crud.get_user_all_tasks(session, UserSchmExtended.model_validate(user))


@router.get("/", response_model=Sequence[TaskSchm])
async def get_user_all_tasks(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    return await crud.get_user_all_tasks(session, user)


@router.post(
    "/",
    response_model=TaskSchm,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_input: CreateTaskSchm,
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    return await crud.create_task(session, task_input, user)


@router.patch("/{task_id}/", response_model=TaskSchm)
async def update_task(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    task_input: UpdateTaskSchm,
    task_id: int,
    user: Annotated[UserSchmExtended, Depends(get_currant_auth_user)],
):
    task_to_update: Task = await crud.get_task_by_id(session, task_id)
    if task_to_update.user_id == user.id or user.role == settings.roles.admin:
        return await crud.update_task(session, task_to_update, task_input)
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="not enough privileges",
    )
