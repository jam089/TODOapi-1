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
