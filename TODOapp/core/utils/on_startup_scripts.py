from api.schemas.user import CreateAdminUserSchm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.crud.user import create_user, get_user_by_id, update_role


async def check_and_create_superuser(
    session: AsyncSession,
    admin_id: int = -1,
    username: str = "TODOadmin",
    password: str = "admin",
) -> str:
    if await get_user_by_id(session, admin_id):
        return "admin is exist"
    admin = CreateAdminUserSchm(
        id=admin_id,
        username=username,
        name=username,
        password=password,
        b_date=None,
        active=True,
    )

    await create_user(session, admin)
    admin_user = await get_user_by_id(session, admin_id)
    if admin_user:
        await update_role(session, admin_user, role=settings.roles.admin)

    return "admin created"
