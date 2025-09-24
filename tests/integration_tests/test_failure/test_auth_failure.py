import pytest
from httpx import AsyncClient

from core.config import settings
from api.http_exceptions import inactive_user_exception, unauth_exc


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
    auth_client: AsyncClient,
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
    response = await auth_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=data,
    )

    assert response.status_code == expected_code
    if expected_details:
        assert response.json().get("detail") == expected_details
