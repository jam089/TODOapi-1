import pytest
from httpx import AsyncClient

from core.config import settings
from core.utils.on_startup_scripts import check_and_create_superuser

from tests.helpers import AuthedUser, TestUser


super_user = {
    "id": -2,
    "username": "TODOadmin_for_user_success",
    "password": "admin",
}


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
    update_by_admin_testcase={
        "username": "jackson",
        "name": "Jack N",
    },
)

test_user_john = TestUser(
    username="john_doe",
    password="john_doe",
    new_password="john1234",
    update_testcase={
        "username": "john_doe2",
    },
    update_by_admin_testcase={
        "username": "johnny_d",
        "name": "Johnny",
    },
)

test_users = [test_user_jack, test_user_john]


@pytest.fixture(scope="session", autouse=True)
async def create_superuser(test_session):
    """
    Creating superuser for admin access rights checking
    """
    await check_and_create_superuser(
        test_session,
        admin_id=super_user.get("id"),
        username=super_user.get("username"),
        password=super_user.get("password"),
    )


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
