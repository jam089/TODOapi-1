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
        headers=auth_user.headers,
    )
    assert response.status_code == 200
    assert response.json().get("created_at"), "created_at not exist"
    assert response.json().get("role"), "role not exist"
