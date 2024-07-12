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
