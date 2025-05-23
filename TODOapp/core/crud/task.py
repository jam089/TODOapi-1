from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from core.models import Task, User
from api.schemas import (
    CreateTaskSchm,
    UpdateTaskSchm,
    SearchTaskSchm,
    UserSchmExtended,
)


async def get_all_tasks(session: AsyncSession) -> Sequence[Task]:
    stmt = select(Task).order_by(Task.user_id, Task.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()


async def get_user_all_tasks(
    session: AsyncSession,
    user: UserSchmExtended,
) -> Sequence[Task]:
    stmt = select(Task).where(Task.user_id == user.id).order_by(Task.user_id, Task.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()


async def get_task_by_id(session: AsyncSession, task_id: int) -> Task | None:
    return await session.get(Task, task_id)


async def get_tasks_by_some_statement(
    session: AsyncSession,
    search_task: SearchTaskSchm,
) -> Sequence[Task] | None:
    condition = []
    if search_task.id is not None:
        condition.append(Task.id == search_task.id)
    if search_task.name is not None:
        condition.append(Task.name == search_task.name)
    if search_task.user_id is not None:
        condition.append(Task.user_id == search_task.user_id)
    if search_task.status is not None:
        condition.append(Task.status == search_task.status)
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
    user: UserSchmExtended,
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


async def update_task(
    session: AsyncSession,
    task_to_update: Task,
    task_in: UpdateTaskSchm,
) -> Task:
    for name, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task_to_update, name, value)

    await session.commit()
    await session.refresh(task_to_update)
    return task_to_update


async def change_task_user_by_user(
    session: AsyncSession,
    task_to_update: Task,
    new_user: User,
) -> Task:
    task_to_update.user_id = new_user.id
    await session.commit()
    await session.refresh(task_to_update)
    return task_to_update


async def delete_task(
    session: AsyncSession,
    task_to_delete: Task,
) -> None:
    await session.delete(task_to_delete)
    await session.commit()
