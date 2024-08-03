import pytest
from httpx import AsyncClient

from core.config import settings
from core.utils.on_startup_scripts import check_and_create_superuser

from tests.helpers import AuthedUser, TestUser


test_user = TestUser(
    username="falter_user",
    name="Falter User",
    b_date="1000-10-10",
    password="falter",
)


@pytest.fixture(scope="session", autouse=True)
async def create_test_user(async_client):
    response = await async_client.post(
        url=f"{settings.api.user.prefix}/",
        json=test_user.json(),
    )


@pytest.fixture(scope="session", autouse=True)
async def create_superuser(test_session):
    """
    Creating superuser for admin access rights checking
    """
    await check_and_create_superuser(test_session)


@pytest.fixture(scope="session")
async def auth_user(async_client: AsyncClient):
    """
    Get loging test users
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
    request_json = {
        "username": "TODOadmin",
        "password": "admin",
    }
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
