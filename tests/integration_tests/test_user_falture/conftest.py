import pytest
from httpx import AsyncClient

from core.crud.user import create_user, delete_user, get_user_by_id
from api.schemas.user import CreateUserSchm
from core.config import settings
from core.utils.on_startup_scripts import check_and_create_superuser

from tests.helpers import AuthedUser, TestUser

super_user = {
    "id": -1,
    "username": "TODOadmin_for_user_failure",
    "password": "admin",
}

test_user = TestUser(
    username="falter_user_for_user_endpoint",
    name="Falter User",
    b_date="1000-10-10",
    password="falter",
)


@pytest.fixture(scope="session", autouse=True)
async def create_test_user(async_client, test_session, request):
    """
    Creating test user for user access rights checking
    """
    user_schm = CreateUserSchm(**test_user.json())
    user = await create_user(test_session, user_schm)

    yield user

    if not request.config.getoption("--skip-delete-endpoints"):
        await delete_user(test_session, user)


@pytest.fixture(scope="session", autouse=True)
async def create_superuser(test_session, request):
    """
    Creating superuser for admin access rights checking
    """
    await check_and_create_superuser(
        test_session,
        admin_id=super_user.get("id"),
        username=super_user.get("username"),
        password=super_user.get("password"),
    )

    s_user = await get_user_by_id(test_session, super_user.get("id"))

    yield s_user

    if not request.config.getoption("--skip-delete-endpoints"):
        await delete_user(test_session, s_user)


@pytest.fixture(scope="session")
async def auth_user(async_client: AsyncClient):
    """
    Get logging test users
    """
    request_json = {
        "username": test_user.username,
        "password": test_user.password,
    }
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=request_json,
    )
    return AuthedUser(
        user=test_user,
        access_token=response.json().get("access_token"),
        refresh_token=response.json().get("refresh_token"),
    )


@pytest.fixture(scope="session")
async def auth_superuser(async_client: AsyncClient):
    request_json = super_user
    request_json.pop("id")
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=request_json,
    )
    s_user = TestUser(*request_json)
    return AuthedUser(
        user=s_user,
        access_token=response.json().get("access_token"),
        refresh_token=response.json().get("refresh_token"),
    )
