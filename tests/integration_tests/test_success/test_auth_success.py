import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_endpoint_auth_user_login(
    async_client: AsyncClient,
    test_user,
):
    login_data = {
        "username": test_user.get("user").username,
        "password": test_user.get("password"),
    }
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=login_data,
    )

    assert response.status_code == 200
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()
    assert "set-cookie" in response.headers


@pytest.mark.asyncio
async def test_endpoint_auth_user_refresh(
    async_client: AsyncClient,
    test_user,
):
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/refresh/",
        cookies={"refresh_token": test_user.get("refresh_token")},
    )
    assert response.status_code == 200
    assert "access_token" in response.json().keys()
    assert "set-cookie" in response.headers


@pytest.mark.asyncio
async def test_endpoint_auth_user_logout(
    async_client: AsyncClient,
    test_user,
):
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/logout/",
        headers=test_user.get("headers"),
    )

    assert response.status_code == 200
    assert response.json().get("detail") == "Logout successful"
    cookies = response.headers.get("set-cookie")
    assert "Max-Age=0" in cookies
