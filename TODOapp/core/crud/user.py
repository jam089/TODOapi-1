from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result, ScalarResult

from core.models import User
from api.schemas import CreateUserSchm, UpdateUserSchm


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).order_by(User.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()
