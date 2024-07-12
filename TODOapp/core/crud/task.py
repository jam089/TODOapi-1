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
