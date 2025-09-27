from collections.abc import Sequence

from api.schemas import CreateAdminUserSchm, CreateUserSchm, UpdateUserSchm
from sqlalchemy import Result, ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.utils.jwt import hash_password


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).order_by(User.id)
    result: ScalarResult = await session.scalars(stmt)
    return result.all()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_username(
    session: AsyncSession,
    username: str,
) -> User | None:
    stmt = select(User).where(User.username == username)
    result: Result = await session.execute(stmt)
    user: User | None = result.scalar_one_or_none()
    return user


async def _create_user_helper(
    session: AsyncSession,
    user_input: dict,
) -> User:
    user_input_w_hashed_password = user_input.copy()
    user_input_w_hashed_password.update(
        password=hash_password(user_input["password"]).decode(),
    )
    new_user = User(**user_input_w_hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def create_user(
    session: AsyncSession,
    user_input: CreateUserSchm,
) -> User:
    return await _create_user_helper(session, user_input.model_dump())


async def create_admin_user(
    session: AsyncSession,
    user_input: CreateAdminUserSchm,
) -> User:
    return await _create_user_helper(session, user_input.model_dump())


async def update_user(
    session: AsyncSession,
    user_to_update: User,
    user_input: UpdateUserSchm,
) -> User:
    for name, value in user_input.model_dump(exclude_unset=True).items():
        setattr(user_to_update, name, value)

    await session.commit()
    await session.refresh(user_to_update)
    return user_to_update


async def update_password(
    session: AsyncSession,
    user_to_update: User,
    password: str | bytes,
) -> User:
    user_to_update.password = hash_password(password).decode()
    await session.commit()
    await session.refresh(user_to_update)
    return user_to_update


async def update_role(
    session: AsyncSession,
    user_to_update: User,
    role: str,
) -> User:
    user_to_update.role = role
    await session.commit()
    await session.refresh(user_to_update)
    return user_to_update


async def delete_user(
    session: AsyncSession,
    user_to_delete: User,
) -> None:
    await session.delete(user_to_delete)
    await session.commit()
