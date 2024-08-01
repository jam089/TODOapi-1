from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from core.config import settings
from main import todo_app

from tests.helpers import AuthedUser


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(todo_app),
        base_url=f"http://test{settings.api.prefix}",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac


def users_for_tests():
    users = [
        {
            "username": "jack_n",
            "name": "Jack Nicholson",
            "b_date": "1937-04-22",
            "password": "jack",
        },
        {
            "username": "john_doe",
            "password": "john_doe",
        },
    ]
    for user in users:
        yield user


@pytest.fixture(params=users_for_tests())
def for_sequenced_user_tests(request):
    return request.param


@pytest.fixture
async def auth_user(async_client: AsyncClient, for_sequenced_user_tests):
    request_json = {
        "username": for_sequenced_user_tests.get("username"),
        "password": for_sequenced_user_tests.get("password"),
    }
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=request_json,
    )
    return AuthedUser(
        username=for_sequenced_user_tests.get("username"),
        password=for_sequenced_user_tests.get("password"),
        access_token=response.json().get("access_token"),
        refresh_token=response.json().get("refresh_token"),
    )
