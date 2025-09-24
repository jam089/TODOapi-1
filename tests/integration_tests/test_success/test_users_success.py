import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.crud.user import get_all_users


@pytest.mark.asyncio
async def test_endpoint_get_profile(async_client: AsyncClient, test_user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/profile/",
        headers=test_user.get("headers"),
    )
    assert response.status_code == 200
    assert response.json().get("id"), "'id' field not exist"
    assert response.json().get("created_at"), "'created_at' field not exist"
    assert response.json().get("role"), "'role' field not exist"


@pytest.mark.asyncio
async def test_endpoint_get_user_by_username(async_client: AsyncClient, test_user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/{test_user.get("user").username}/",
    )
    assert response.status_code == 200
    assert response.json().get("username") == test_user.get("user").username
    assert response.json().get("name") == test_user.get("user").name
    if test_user.get("user").b_date:
        assert (
            datetime.date.fromisoformat(response.json().get("b_date"))
            == test_user.get("user").b_date
        )
    assert response.json().get("active"), "'active' field not exist"


@pytest.mark.asyncio
async def test_endpoint_get_all_users(
    async_client: AsyncClient,
    test_session: AsyncSession,
    test_user_a,
    test_user_b,
):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/",
        headers=test_user_a.get("headers"),
    )
    assert response.status_code == 200

    expected_users_list = await get_all_users(test_session)
    expected = {(user.id, user.username) for user in expected_users_list}
    actual = {(user.get("id"), user.get("username")) for user in response.json()}
    assert actual == expected


@pytest.mark.asyncio
async def test_admin_endpoint_get_user_by_id(async_client, admin_user, test_user):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/",
        params={
            "user_id": test_user.get("user").id,
        },
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 200
    assert response.json().get("username") == test_user.get("user").username
    assert response.json().get("name") == test_user.get("user").name
    if test_user.get("user").b_date:
        assert (
            datetime.date.fromisoformat(response.json().get("b_date"))
            == test_user.get("user").b_date
        )
    assert response.json().get("id") == test_user.get("user").id
    assert response.json().get("active"), "'active' field not exist"
    assert response.json().get("created_at"), "'created_at' field not exist"
    assert response.json().get("role"), "'role' field not exist"


@pytest.mark.asyncio
async def test_endpoint_create_user(async_client: AsyncClient, test_user_to_create):
    response = await async_client.post(
        url=f"{settings.api.user.prefix}/",
        json=test_user_to_create,
    )
    assert response.status_code == 201
    assert response.json().get("username") == test_user_to_create.get("username")
    assert response.json().get("name") == test_user_to_create.get("name")
    assert response.json().get("b_date") == test_user_to_create.get("b_date")
    assert response.json().get("active"), "'active' field not exist"


@pytest.mark.asyncio
async def test_endpoint_update_yourself(async_client, test_user):
    update_dict = test_user.get("update_scenarios").get("user")
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/",
        json=update_dict,
        headers=test_user.get("headers"),
    )
    assert response.status_code == 200
    for name, value in update_dict.items():
        assert response.json().get(name) == value
    assert response.json().get("last_update_at"), "'last_update_at' field not exist"


@pytest.mark.asyncio
async def test_endpoint_delete_yourself(async_client, test_user):
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/",
        headers=test_user.get("headers"),
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_endpoint_change_your_password(async_client, auth_client, test_user):
    update_password = "test_pass007"
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/change_password/",
        json={"password": update_password},
        headers=test_user.get("headers"),
    )
    assert response.status_code == 200

    request_json = {
        "username": test_user.get("user").username,
        "password": update_password,
    }
    logging_with_new_pass_response = await auth_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=request_json,
    )
    assert logging_with_new_pass_response.status_code == 200


@pytest.mark.asyncio
async def test_admin_endpoint_change_role(
    async_client,
    test_user,
    admin_user,
):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/{test_user.get("user").id}/role/",
        json={"role": settings.roles.admin},
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 200
    assert response.json().get("username") == test_user.get("user").username
    assert response.json().get("name") == test_user.get("user").name
    if test_user.get("user").b_date:
        assert (
            datetime.date.fromisoformat(response.json().get("b_date"))
            == test_user.get("user").b_date
        )
    assert response.json().get("id") == test_user.get("user").id
    assert response.json().get("role") == settings.roles.admin
    assert response.json().get("created_at"), "'created_at' filed not exist"
    assert response.json().get("last_update_at"), "'last_update_at' filed not exist"
    assert response.json().get("active"), "'active' filed not exist"


@pytest.mark.asyncio
async def test_admin_endpoint_update_user(
    async_client,
    test_user,
    admin_user,
):
    update_dict = test_user.get("update_scenarios").get("admin")
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/{test_user.get("user").id}/",
        json=update_dict,
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 200
    for name, value in update_dict.items():
        assert response.json().get(name) == value
    assert response.json().get("last_update_at"), "'last_update_at' field not exist"


@pytest.mark.asyncio
async def test_admin_endpoint_delete_user(async_client, test_user, admin_user):
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/{test_user.get("user").id}/",
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 204
