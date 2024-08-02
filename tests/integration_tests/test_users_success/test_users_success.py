import pytest
from httpx import AsyncClient

from core.config import settings

from integration_tests.test_users_success.conftest import test_users


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
    assert response.json().get("active"), "'active' field not exist"


@pytest.mark.parametrize("user", test_users)
async def test_endpoint_get_user_by_username(async_client: AsyncClient, user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/{user.username}/",
    )
    assert response.status_code == 200
    assert response.json().get("username") == user.username
    assert response.json().get("name") == user.name
    assert response.json().get("b_date") == user.b_date
    assert response.json().get("active"), "'active' field not exist"


async def test_endpoint_get_profile(async_client: AsyncClient, auth_user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/profile/",
        headers=auth_user.headers,
    )
    assert response.status_code == 200
    assert response.json().get("id"), "'id' field not exist"
    for test_user in test_users:
        if test_user.username == auth_user.user.username:
            test_user.user_id = response.json().get("id")
            auth_user.user.user_id = response.json().get("id")
    assert response.json().get("created_at"), "'created_at' field not exist"
    assert response.json().get("role"), "'role' field not exist"


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
        assert json.get("active"), "'active' field not exist"


async def test_admin_endpoint_get_user_by_id(
    async_client, auth_superuser, for_sequenced_user_tests
):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/",
        params={
            "id": for_sequenced_user_tests.user_id,
        },
        headers=auth_superuser.headers,
    )
    assert response.status_code == 200
    assert response.json().get("username") == for_sequenced_user_tests.username
    assert response.json().get("name") == for_sequenced_user_tests.name
    assert response.json().get("b_date") == for_sequenced_user_tests.b_date
    assert response.json().get("id") == for_sequenced_user_tests.user_id
    assert response.json().get("active"), "'active' field not exist"
    assert response.json().get("created_at"), "'created_at' field not exist"
    assert response.json().get("role"), "'role' field not exist"


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
    assert response.json().get("last_update_at"), "'last_update_at' field not exist"


async def test_endpoint_change_your_password(async_client, auth_user):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/change_password/",
        json={"password": auth_user.user.password},
        headers=auth_user.headers,
    )
    assert response.status_code == 200

    for test_user in test_users:
        if test_user.username == auth_user.user.username:
            test_user.update_password()
            auth_user.user.update_password()


async def test_admin_endpoint_change_role(
    async_client,
    auth_superuser,
    for_sequenced_user_tests,
):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/{for_sequenced_user_tests.user_id}/role/",
        json={"role": settings.roles.admin},
        headers=auth_superuser.headers,
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get("username") == for_sequenced_user_tests.username
    assert response.json().get("name") == for_sequenced_user_tests.name
    assert response.json().get("b_date") == for_sequenced_user_tests.b_date
    assert response.json().get("id") == for_sequenced_user_tests.user_id
    assert response.json().get("role") == settings.roles.admin
    assert response.json().get("created_at"), "'created_at' filed not exist"
    assert response.json().get("last_update_at"), "'last_update_at' filed not exist"
    assert response.json().get("active"), "'active' filed not exist"


async def test_admin_endpoint_update_user(
    async_client,
    auth_superuser,
    for_sequenced_user_tests,
):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/{for_sequenced_user_tests.user_id}/",
        json=for_sequenced_user_tests.update_by_admin_testcase,
        headers=auth_superuser.headers,
    )
    assert response.status_code == 200

    for test_user in test_users:
        if test_user.username == for_sequenced_user_tests.username:
            test_user.update_user(admin_flg=True)
            for_sequenced_user_tests.update_user(admin_flg=True)
    for name, value in for_sequenced_user_tests.update_by_admin_testcase.items():
        assert response.json().get(name) == value
    assert response.json().get("last_update_at"), "'last_update_at' field not exist"


async def test_endpoint_delete_yourself(async_client, auth_user):
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/",
        headers=auth_user.headers,
    )
    assert response.status_code == 204


async def test_admin_endpoint_delete_user(async_client, auth_superuser):
    admin_id = -1
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/{admin_id}/",
        headers=auth_superuser.headers,
    )
    assert response.status_code == 204
