from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result, ScalarResult

from core.models import User
from api.schemas import CreateUserSchm, UpdateUserSchm


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).order_by(User.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def create_user(
    session: AsyncSession,
    user_input: CreateUserSchm,
) -> User:
    new_user = User(**user_input.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
