import pytest
from httpx import AsyncClient

from core.config import settings

from integration_tests.test_user_falture.conftest import test_user


async def test_endpoint_create_user(async_client: AsyncClient):
    response = await async_client.post(
        url=f"{settings.api.user.prefix}/",
        json={},
    )
    assert response.status_code == 422


async def test_endpoint_get_user_by_username(async_client: AsyncClient):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/invalid_username/",
    )
    assert response.status_code == 404


async def test_endpoint_get_profile(async_client: AsyncClient):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/profile/",
    )
    assert response.status_code == 401


async def test_endpoint_get_all_users(async_client: AsyncClient):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/",
    )
    assert response.status_code == 401


@pytest.mark.parametrize("admin_flg", [False, True])
async def test_admin_endpoint_get_user_by_id(
    async_client,
    auth_superuser,
    auth_user,
    admin_flg,
):
    if admin_flg:
        response = await async_client.get(
            url=f"{settings.api.user.prefix}/",
            params={
                "id": -3,
            },
            headers=auth_user.headers,
        )
        assert response.status_code == 403
    else:
        response = await async_client.get(
            url=f"{settings.api.user.prefix}/",
            params={
                "id": -3,
            },
            headers=auth_superuser.headers,
        )
        assert response.status_code == 404


async def test_endpoint_update_yourself(
    async_client,
    auth_user,
):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/",
        json={},
    )
    assert response.status_code == 401


async def test_endpoint_change_your_password(async_client, auth_user):
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/change_password/",
        json={},
    )
    assert response.status_code == 401


@pytest.mark.parametrize("switch", [422, 404, 403])
async def test_admin_endpoint_change_role(
    async_client,
    auth_superuser,
    auth_user,
    switch,
):
    if switch == 422:
        response = await async_client.patch(
            url=f"{settings.api.user.prefix}/{test_user.user_id}/role/",
            json={"role": "stupid"},
            headers=auth_superuser.headers,
        )
        assert response.status_code == 422
    elif switch == 404:
        response = await async_client.patch(
            url=f"{settings.api.user.prefix}/-28/role/",
            json={"role": settings.roles.admin},
            headers=auth_superuser.headers,
        )
        assert response.status_code == 404
    elif switch == 403:
        response = await async_client.patch(
            url=f"{settings.api.user.prefix}/{test_user.user_id}/role/",
            json={"role": settings.roles.admin},
            headers=auth_user.headers,
        )
        assert response.status_code == 403


@pytest.mark.parametrize("switch", [404, 403])
async def test_admin_endpoint_update_user(
    async_client,
    auth_superuser,
    auth_user,
    switch,
):
    if switch == 404:
        response = await async_client.patch(
            url=f"{settings.api.user.prefix}/-28/role/",
            json={},
            headers=auth_superuser.headers,
        )
        assert response.status_code == 404
    elif switch == 403:
        response = await async_client.patch(
            url=f"{settings.api.user.prefix}/{test_user.user_id}/role/",
            json={},
            headers=auth_user.headers,
        )
        assert response.status_code == 403


async def test_endpoint_delete_yourself(async_client, auth_user):
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/",
    )
    assert response.status_code == 401


@pytest.mark.parametrize("admin_flg", [False, True])
async def test_admin_endpoint_delete_user(
    async_client, auth_superuser, auth_user, admin_flg
):
    if admin_flg:
        response = await async_client.delete(
            url=f"{settings.api.user.prefix}/-30/",
            headers=auth_superuser.headers,
        )
        assert response.status_code == 404
    else:
        admin_id = -1
        response = await async_client.delete(
            url=f"{settings.api.user.prefix}/{admin_id}/",
            headers=auth_user.headers,
        )
        assert response.status_code == 403
