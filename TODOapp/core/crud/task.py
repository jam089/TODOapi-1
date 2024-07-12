from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from core.models import Task, User
from api.schemas import (
    CreateTaskSchm,
    UpdateTaskSchm,
    ChangeTaskUserSchm,
    SearchTaskSchm,
)


async def get_all_tasks(session: AsyncSession) -> Sequence[Task]:
    stmt = select(Task).order_by(Task.user_id, Task.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()


async def get_task_by_id(session: AsyncSession, task_id: int) -> Task | None:
    return await session.get(Task, task_id)


async def get_task_by_user(
    session: AsyncSession,
    user: User,
) -> Sequence[Task] | None:
    stmt = select(Task).where(Task.user_id == user.id).order_by(Task.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()


async def get_tasks_by_some_statement(
    session: AsyncSession,
    search_task: SearchTaskSchm,
) -> Sequence[Task] | None:
    condition = []
    if search_task.id is not None:
        condition.append(Task.id == search_task.id)
    if search_task.name is not None:
        condition.append(Task.name == search_task.name)
    if search_task.start_at is not None:
        condition.append(Task.start_at >= search_task.id)
    if search_task.end_at is not None:
        condition.append(Task.end_at <= search_task.end_at)

    stmt = select(Task).where(*condition).order_by(Task.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()


async def create_task(
    session: AsyncSession,
    task_input: CreateTaskSchm,
    user: User,
) -> Task:
    new_task_dict = {
        "user_id": user.id,
        **task_input.model_dump(),
    }
    new_task = Task(**new_task_dict)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task
