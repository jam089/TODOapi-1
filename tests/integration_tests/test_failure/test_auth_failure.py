import pytest
from api.http_exceptions import (
    inactive_user_exception,
    token_invalid_exc,
    unauth_exc,
)
from core.config import settings
from httpx import AsyncClient


@pytest.mark.parametrize(
    "mutated_user, expected_code, expected_details",
    [
        ({"target": "json_none"}, 422, None),
        (
            {"target": "user", "attrs": {"active": False}},
            401,
            inactive_user_exception.detail,
        ),
        (
            {"target": "wrong_password", "value": "wrong_pass"},
            401,
            unauth_exc.detail,
        ),
        (
            {"target": "wrong_username", "value": "wrong_login"},
            401,
            unauth_exc.detail,
        ),
    ],
    indirect=["mutated_user"],
)
@pytest.mark.asyncio
async def test_endpoint_auth_user_login(
    async_client: AsyncClient,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    wrong_pass = mutated_user.get("wrong_password")
    wrong_username = mutated_user.get("wrong_username")
    password = wrong_pass if wrong_pass else mutated_user.get("password")
    username = wrong_username if wrong_username else mutated_user.get("user").username
    login_data = {
        "username": username,
        "password": password,
    }
    data = None if mutated_user.get("json_none") else login_data
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=data,
    )

    assert response.status_code == expected_code
    if expected_details:
        assert response.json().get("detail") == expected_details
    assert "access_token" not in response.json()
    assert "refresh_token" not in response.json()
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize(
    "mutated_user, expected_code, expected_details",
    [
        (
            {"target": "refresh_token", "value": "wrong_refresh_token"},
            401,
            token_invalid_exc.detail,
        ),
        (
            {"target": "headers_none"},
            401,
            token_invalid_exc.detail,
        ),
        (
            {"target": "user", "attrs": {"active": False}},
            401,
            inactive_user_exception.detail,
        ),
    ],
    indirect=["mutated_user"],
)
@pytest.mark.asyncio
async def test_endpoint_auth_user_refresh(
    async_client: AsyncClient,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    cookies_dict = {"refresh_token": mutated_user.get("refresh_token")}
    cookies = None if mutated_user.get("headers") is None else cookies_dict
    if cookies:
        async_client.cookies.update(cookies)
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/refresh/",
    )
    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details
    assert "access_token" not in response.json()
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize(
    "mutated_user, expected_code, expected_details",
    [
        (
            {"target": "access_token", "value": "wrong_token"},
            401,
            token_invalid_exc.detail,
        ),
        (
            {"target": "user", "attrs": {"active": False}},
            401,
            inactive_user_exception.detail,
        ),
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
    ],
    indirect=["mutated_user"],
)
@pytest.mark.asyncio
async def test_endpoint_auth_user_logout(
    async_client: AsyncClient,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/logout/",
        headers=mutated_user.get("headers"),
    )

    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details
    assert response.json().get("detail") != "Logout successful"
    assert response.headers.get("set-cookie") is None
