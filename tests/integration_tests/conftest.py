from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from core.config import settings
from core.utils.on_startup_scripts import check_and_create_superuser
from main import todo_app

from tests.helpers import AuthedUser, TestUser


test_user_jack = TestUser(
    username="jack_n",
    name="Jack Nicholson",
    b_date="1937-04-22",
    password="jack",
    new_password="jack1234",
    update_testcase={
        "username": "jack_nicholson",
        "name": "Jack Nicholson",
        "b_date": "2000-12-01",
        "active": True,
    },
)

test_user_john = TestUser(
    username="john_doe",
    password="john_doe",
    new_password="john1234",
    update_testcase={
        "username": "john_doe2",
    },
)

test_users = [test_user_jack, test_user_john]


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Creating async test client
    """
    async with AsyncClient(
        transport=ASGITransport(todo_app),
        base_url=f"http://test{settings.api.prefix}",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def create_superuser(test_session):
    """
    Creating superuser for admin access rights checking
    """
    await check_and_create_superuser(test_session)


@pytest.fixture(scope="session", params=test_users)
def for_sequenced_user_tests(request) -> TestUser:
    """
    Fixture which return one test user for sequence of tests
    """
    return request.param


@pytest.fixture(scope="session")
async def auth_user(async_client: AsyncClient, for_sequenced_user_tests):
    """
    Get loging test users
    """
    request_json = {
        "username": for_sequenced_user_tests.username,
        "password": for_sequenced_user_tests.password,
    }
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=request_json,
    )
    return AuthedUser(
        user=for_sequenced_user_tests,
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
