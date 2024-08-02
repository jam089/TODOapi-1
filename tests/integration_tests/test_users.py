import pytest
from httpx import AsyncClient

from core.config import settings

from tests.integration_tests.conftest import test_users


@pytest.mark.parametrize("user", test_users)
async def test_endpoint_create_user(async_client: AsyncClient, user):
    response = await async_client.post(
        url=f"{settings.api.user.prefix}/",
        json=user.json(),
    )
    assert response.status_code == 201
    assert response.json().get("username") == user.username
    assert response.json().get("name") == user.name
    assert response.json().get("b_date") == user.b_date
    assert response.json().get("active"), "active not exist"


@pytest.mark.parametrize("user", test_users)
async def test_endpoint_get_user_by_username(async_client: AsyncClient, user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/{user.username}/",
    )
    assert response.status_code == 200
    assert response.json().get("username") == user.username
    assert response.json().get("name") == user.name
    assert response.json().get("b_date") == user.b_date
    assert response.json().get("active"), "active not exist"


async def test_endpoint_get_profile(async_client: AsyncClient, auth_user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/profile/",
        headers=auth_user.headers,
    )
    assert response.status_code == 200
    assert response.json().get("created_at"), "created_at not exist"
    assert response.json().get("role"), "role not exist"


async def test_endpoint_get_all_users(async_client: AsyncClient, auth_user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/",
        headers=auth_user.headers,
    )
    assert response.status_code == 200

    expected_list = ["TODOadmin"]
    for user in test_users:
        expected_list.append(user.username)

    for json in response.json():  # type: dict
        assert json.get("username") in expected_list
        assert json.get("active"), "active not exist"


async def test_endpoint_update_yourself(async_client, auth_user):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/",
        json=auth_user.user.update_testcase,
        headers=auth_user.headers,
    )
    assert response.status_code == 200

    for test_user in test_users:
        if test_user.username == auth_user.user.username:
            test_user.update_user()
            auth_user.user.update_user()
    for name, value in auth_user.user.update_testcase.items():
        assert response.json().get(name) == value
    assert response.json().get("last_update_at"), "last_update_at not exist"


async def test_endpoint_change_your_password(async_client, auth_user):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/change_password/",
        json={
            "password": auth_user.user.password,
        },
        headers=auth_user.headers,
    )
    assert response.status_code == 200

    for test_user in test_users:
        if test_user.username == auth_user.user.username:
            test_user.update_password()
            auth_user.user.update_password()


async def test_endpoint_delete_yourself(async_client, auth_user):
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/",
        headers=auth_user.headers,
    )
    assert response.status_code == 204
