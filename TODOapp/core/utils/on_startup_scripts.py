from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.crud.user import create_user, update_role, get_user_by_id
from api.schemas.user import CreateAdminUserSchm


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
    await update_role(session, admin_user, role=settings.roles.admin)

    return "admin created"
