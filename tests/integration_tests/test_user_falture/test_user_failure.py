import pytest
from httpx import AsyncClient

from core.config import settings
from api.http_exceptions import (
    rendering_exception_with_param,
    token_invalid_exc,
    inactive_user_exception,
    user_exception_templ,
    no_priv_except,
    user_id_exc_templ,
    username_already_exist_exc_templ,
    role_not_exist_exc_templ,
)


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
async def test_endpoint_get_profile(
    async_client: AsyncClient,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/profile/",
        headers=mutated_user.get("headers"),
    )
    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details


@pytest.mark.asyncio
async def test_endpoint_get_user_by_username(async_client: AsyncClient):
    username = "invalid_username"
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/{username}/",
    )
    exc = rendering_exception_with_param(user_exception_templ, username)
    assert response.status_code == 404
    assert response.json().get("detail") == exc.detail


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
async def test_endpoint_get_all_users(
    async_client: AsyncClient,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/",
        headers=mutated_user.get("headers"),
    )

    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_admin, expected_code, expected_details",
    [
        (
            {
                "user_fixture": "admin_user",
                "target": "access_token",
                "value": "wrong_token",
            },
            401,
            token_invalid_exc.detail,
        ),
        (
            {"target": "user", "attrs": {"active": False}},
            401,
            inactive_user_exception.detail,
        ),
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
        (
            {"target": "wrong_user_id_to_request", "value": 999},
            404,
            user_id_exc_templ.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_admin_endpoint_get_user_by_id(
    async_client: AsyncClient,
    mutated_admin: dict,
    expected_code,
    expected_details,
    test_user_a,
):
    wrong_id = mutated_admin.get("wrong_user_id_to_request")
    request_user_id = wrong_id if wrong_id else test_user_a.get("user").id
    response = await async_client.get(
        url=f"{settings.api.user.prefix}/",
        params={
            "user_id": int(request_user_id),
        },
        headers=mutated_admin.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == user_id_exc_templ.detail:
        exc = rendering_exception_with_param(user_id_exc_templ, request_user_id)
        assert response.json().get("detail") == exc.detail
    else:
        assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "json, expected_code, expected_details",
    [
        (
            {
                "name": "test",
                "b_date": "2000-09-23",
                "password": "test",
            },
            409,
            username_already_exist_exc_templ.detail,
        ),
        (None, 422, None),
    ],
)
@pytest.mark.asyncio
async def test_endpoint_create_user(
    async_client: AsyncClient,
    test_user_a,
    json,
    expected_code,
    expected_details,
):
    if json:
        json.update({"username": test_user_a.get("user").username})
    else:
        json = None
    response = await async_client.post(
        url=f"{settings.api.user.prefix}/",
        json=json,
    )
    assert response.status_code == expected_code
    if json is not None:
        exc = rendering_exception_with_param(
            username_already_exist_exc_templ, test_user_a.get("user").username
        )
        assert response.json().get("detail") == exc.detail


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
        ({"target": "json_none"}, 422, None),
        (
            {"target": "user_already_exist"},
            409,
            username_already_exist_exc_templ.detail,
        ),
    ],
    indirect=["mutated_user"],
)
@pytest.mark.asyncio
async def test_endpoint_update_yourself(
    async_client: AsyncClient,
    admin_user,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    json = mutated_user.get("update_scenarios")
    if mutated_user.get("json_none"):
        json = None
    elif mutated_user.get("user_already_exist"):
        json.update({"username": admin_user.get("user").username})
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/",
        json=json,
        headers=mutated_user.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == username_already_exist_exc_templ.detail:
        exc = rendering_exception_with_param(
            username_already_exist_exc_templ, admin_user.get("user").username
        )
        assert response.json().get("detail") == exc.detail
    elif json is None:
        ...
    else:
        assert response.json().get("detail") == expected_details


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
async def test_endpoint_delete_yourself(
    async_client,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/",
        headers=mutated_user.get("headers"),
    )
    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details


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
        ({"target": "json_none"}, 422, None),
    ],
    indirect=["mutated_user"],
)
@pytest.mark.asyncio
async def test_endpoint_change_your_password(
    async_client,
    mutated_user: dict,
    expected_code,
    expected_details,
):
    json = {"password": "test_pass"} if not mutated_user.get("json_none") else None
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/change_password/",
        json=json,
        headers=mutated_user.get("headers"),
    )
    assert response.status_code == expected_code
    if not mutated_user.get("json_none"):
        assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_admin, expected_code, expected_details",
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
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        ({"target": "json_none"}, 422, None),
        (
            {"target": "wrong_role_to_request", "value": "Boss"},
            400,
            role_not_exist_exc_templ.detail,
        ),
        (
            {"target": "wrong_user_id_to_request", "value": "999"},
            404,
            user_id_exc_templ.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_admin_endpoint_change_role(
    async_client: AsyncClient,
    test_user_a,
    mutated_admin: dict,
    expected_code,
    expected_details,
):
    wrong_role_to_request = mutated_admin.get("wrong_role_to_request")
    wrong_user_id = mutated_admin.get("wrong_user_id_to_request")
    role_for_update = (
        wrong_role_to_request if wrong_role_to_request else settings.roles.admin
    )
    json = None if mutated_admin.get("json_none") else {"role": role_for_update}
    user_to_update = wrong_user_id if wrong_user_id else test_user_a.get("user").id
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/{user_to_update}/role/",
        json=json,
        headers=mutated_admin.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == user_id_exc_templ.detail:
        exc = rendering_exception_with_param(user_id_exc_templ, wrong_user_id)
        assert response.json().get("detail") == exc.detail
    elif expected_details == role_not_exist_exc_templ.detail:
        exc = rendering_exception_with_param(
            role_not_exist_exc_templ, wrong_role_to_request
        )
        assert response.json().get("detail") == exc.detail
    elif expected_details is None:
        ...
    else:
        assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_admin, expected_code, expected_details",
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
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        ({"target": "json_none"}, 422, None),
        (
            {"target": "user_already_exist"},
            409,
            username_already_exist_exc_templ.detail,
        ),
        (
            {"target": "wrong_user_id_to_request", "value": "999"},
            404,
            user_id_exc_templ.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_admin_endpoint_update_user(
    async_client: AsyncClient,
    test_user,
    mutated_admin: dict,
    expected_code,
    expected_details,
):
    wrong_user_id = mutated_admin.get("wrong_user_id_to_request")
    update_scenario = test_user.get("update_scenarios").get("admin")
    json = None if mutated_admin.get("json_none") else update_scenario
    if mutated_admin.get("user_already_exist"):
        json.update({"username": mutated_admin.get("user").username})
    user_to_update = wrong_user_id if wrong_user_id else test_user.get("user").id
    response = await async_client.patch(
        url=f"{settings.api.user.prefix}/{user_to_update}/",
        json=json,
        headers=mutated_admin.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == user_id_exc_templ.detail:
        exc = rendering_exception_with_param(user_id_exc_templ, wrong_user_id)
        assert response.json().get("detail") == exc.detail
    elif expected_details == username_already_exist_exc_templ.detail:
        exc = rendering_exception_with_param(
            username_already_exist_exc_templ, update_scenario.get("username")
        )
        assert response.json().get("detail") == exc.detail
    elif expected_details is None:
        ...
    else:
        assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_admin, expected_code, expected_details",
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
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "wrong_user_id_to_request", "value": "999"},
            404,
            user_id_exc_templ.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_admin_endpoint_delete_user(
    async_client: AsyncClient,
    test_user,
    mutated_admin: dict,
    expected_code,
    expected_details,
):
    wrong_user_id = mutated_admin.get("wrong_user_id_to_request")
    user_to_update = wrong_user_id if wrong_user_id else test_user.get("user").id
    response = await async_client.delete(
        url=f"{settings.api.user.prefix}/{user_to_update}/",
        headers=mutated_admin.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == user_id_exc_templ.detail:
        exc = rendering_exception_with_param(user_id_exc_templ, wrong_user_id)
        assert response.json().get("detail") == exc.detail
    else:
        assert response.json().get("detail") == expected_details
