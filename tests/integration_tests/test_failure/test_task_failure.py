from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.http_exceptions import (
    rendering_exception_with_param,
    token_invalid_exc,
    inactive_user_exception,
    no_priv_except,
    user_id_exc_templ,
    task_id_exc_templ,
    status_exception_templ,
)
from api.schemas import UserSchmExtended
from core.config import settings
from api.schemas.task import TaskSchm
from core.crud import task as task_crud


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
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_endpoint_get_all_tasks(
    async_client: AsyncClient,
    test_session: AsyncSession,
    mutated_admin: dict,
    test_task_a: dict,
    test_user_b: dict,
    expected_code,
    expected_details,
):
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/all/",
        headers=mutated_admin.get("headers"),
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
        (
            {
                "target": "wrong_json",
                "value": {
                    "start_at": "Test Task 1 delayed",
                },
            },
            422,
            None,
        ),
        (
            {"target": "wrong_status", "value": {"status": "Not needed"}},
            400,
            status_exception_templ.detail,
        ),
    ],
    indirect=["mutated_user"],
)
@pytest.mark.asyncio
async def test_endpoint_search_task_by_parameters(
    async_client: AsyncClient,
    mutated_user: dict,
    test_multiple_tasks: dict,
    expected_code,
    expected_details,
):
    task = test_multiple_tasks.get("task_list")[2]
    wrong_json = mutated_user.get("wrong_json")
    wrong_status = mutated_user.get("wrong_status")
    if mutated_user.get("json_none"):
        params = None
    elif wrong_json:
        params = wrong_json
    elif wrong_status:
        params = wrong_status
    else:
        params = {"name": task.name, "user_id": task.user_id}
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/search/",
        params=params,
        headers=mutated_user.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == status_exception_templ.detail:
        exc = rendering_exception_with_param(
            status_exception_templ, wrong_status.get("status")
        )
        assert response.json().get("detail") == exc.detail
    elif not expected_details:
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
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
        (
            {"target": "user_id_for_task", "value": 999},
            404,
            user_id_exc_templ.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_endpoint_get_task_by_user_id(
    async_client: AsyncClient,
    test_session: AsyncSession,
    mutated_admin: dict,
    test_task: dict,
    expected_code,
    expected_details,
):
    wrong_user_id = mutated_admin.get("user_id_for_task")
    user_id = wrong_user_id if wrong_user_id else test_task.get("task").user_id
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/by-user/{user_id}/",
        headers=mutated_admin.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == user_id_exc_templ.detail:
        exc = rendering_exception_with_param(user_id_exc_templ, wrong_user_id)
        assert response.json().get("detail") == exc.detail
    else:
        assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_multiple_task, expected_code, expected_details",
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
    indirect=["mutated_multiple_task"],
)
@pytest.mark.asyncio
async def test_endpoint_get_user_all_tasks(
    async_client: AsyncClient,
    mutated_multiple_task: dict,
    expected_code,
    expected_details,
):
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/",
        headers=mutated_multiple_task.get("headers"),
    )
    assert response.status_code == expected_code
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
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
        (
            {"target": "task_id_for_task", "value": 999},
            404,
            task_id_exc_templ.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_endpoint_get_task_by_task_id(
    async_client: AsyncClient,
    test_session: AsyncSession,
    mutated_admin: dict,
    test_task: dict,
    expected_code,
    expected_details,
):
    wrong_task_id = mutated_admin.get("task_id_for_task")
    task_id = wrong_task_id if wrong_task_id else test_task.get("task").id
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/{task_id}/",
        headers=mutated_admin.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == task_id_exc_templ.detail:
        exc = rendering_exception_with_param(task_id_exc_templ, wrong_task_id)
        assert response.json().get("detail") == exc.detail
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
        ({"target": "json_none"}, 422, None),
        (
            {
                "target": "wrong_json",
                "value": {
                    "name": "Test Task 1 delayed",
                    "status": settings.tstat.dly,
                },
            },
            422,
            None,
        ),
    ],
    indirect=["mutated_user"],
)
@pytest.mark.asyncio
async def test_endpoint_create_task(
    async_client: AsyncClient,
    mutated_user: dict,
    test_task_to_create: dict,
    expected_code,
    expected_details,
):
    wrong_task = mutated_user.get("wrong_json")
    task_to_create = wrong_task if wrong_task else test_task_to_create
    json = None if mutated_user.get("json_none") else task_to_create
    response = await async_client.post(
        url=f"{settings.api.task.prefix}/",
        headers=mutated_user.get("headers"),
        json=json,
    )
    assert response.status_code == expected_code
    if expected_details:
        assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_task, expected_code, expected_details",
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
        (
            {"target": "task_id_for_task", "value": 999},
            404,
            task_id_exc_templ.detail,
        ),
        (
            {"target": "user_id_for_task", "value": 999},
            404,
            user_id_exc_templ.detail,
        ),
        ({"target": "json_none"}, 422, None),
        (
            {
                "target": "wrong_json",
                "value": {
                    "name": "Test Task 1 delayed",
                    "status": settings.tstat.dly,
                },
            },
            422,
            None,
        ),
    ],
    indirect=["mutated_task"],
)
@pytest.mark.asyncio
async def test_endpoint_change_task_owner_by_user(
    async_client: AsyncClient,
    mutated_task: dict,
    test_user_c: dict,
    expected_code,
    expected_details,
):
    new_user_id = test_user_c.get("user").id
    wrong_task = mutated_task.get("wrong_json")
    wrong_user_id = mutated_task.get("user_id_for_task")
    task_to_create = wrong_task if wrong_task else {"user_id": new_user_id}
    task_to_create = {"user_id": wrong_user_id} if wrong_user_id else task_to_create
    json = None if mutated_task.get("json_none") else task_to_create
    wrong_task_id = mutated_task.get("task_id_for_task")
    task_id = wrong_task_id if wrong_task_id else mutated_task.get("task").id
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{task_id}/change_owner/",
        headers=mutated_task.get("headers"),
        params=json,
    )
    assert response.status_code == expected_code
    if expected_details == task_id_exc_templ.detail:
        exc = rendering_exception_with_param(task_id_exc_templ, wrong_task_id)
        assert response.json().get("detail") == exc.detail
    elif expected_details == user_id_exc_templ.detail:
        exc = rendering_exception_with_param(user_id_exc_templ, wrong_user_id)
        assert response.json().get("detail") == exc.detail
    elif not expected_details:
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
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_endpoint_change_task_owner_by_admin(
    async_client: AsyncClient,
    mutated_admin: dict,
    test_task: dict,
    test_user_c: dict,
    expected_code,
    expected_details,
):
    new_user_id = test_user_c.get("user").id
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/change_owner/",
        headers=mutated_admin.get("headers"),
        params={"user_id": new_user_id},
    )
    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_task, expected_code, expected_details",
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
        (
            {"target": "task_id_for_task", "value": 999},
            404,
            task_id_exc_templ.detail,
        ),
        (
            {"target": "wrong_status", "value": {"status": "delat ne budu"}},
            400,
            status_exception_templ.detail,
        ),
        ({"target": "json_none"}, 422, None),
        (
            {
                "target": "wrong_json",
                "value": {
                    "name": "Test Task 1 delayed",
                    "end_at": settings.tstat.pld,
                },
            },
            422,
            None,
        ),
    ],
    indirect=["mutated_task"],
)
@pytest.mark.asyncio
async def test_endpoint_update_task_by_user(
    async_client: AsyncClient,
    mutated_task: dict,
    expected_code,
    expected_details,
):
    update_scenario = mutated_task.get("update_scenarios").get("user")
    wrong_task = mutated_task.get("wrong_json")
    wrong_status = mutated_task.get("wrong_status")
    wrong_task_id = mutated_task.get("task_id_for_task")
    if wrong_status:
        json = wrong_status
    elif wrong_task:
        json = wrong_task
    elif mutated_task.get("json_none"):
        json = None
    else:
        json = update_scenario
    task_id = wrong_task_id if wrong_task_id else mutated_task.get("task").id
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{task_id}/",
        headers=mutated_task.get("headers"),
        json=json,
    )
    assert response.status_code == expected_code
    if expected_details == task_id_exc_templ.detail:
        exc = rendering_exception_with_param(task_id_exc_templ, wrong_task_id)
        assert response.json().get("detail") == exc.detail
    elif expected_details == status_exception_templ.detail:
        exc = rendering_exception_with_param(
            status_exception_templ, wrong_status.get("status")
        )
        assert response.json().get("detail") == exc.detail
    elif not expected_details:
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
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_endpoint_update_task_by_admin(
    async_client: AsyncClient,
    mutated_admin: dict,
    test_task: dict,
    expected_code,
    expected_details,
):
    update_scenario = test_task.get("update_scenarios").get("admin")
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/",
        headers=mutated_admin.get("headers"),
        json=update_scenario,
    )
    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details


@pytest.mark.parametrize(
    "mutated_task, expected_code, expected_details",
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
        (
            {"target": "task_id_for_task", "value": 999},
            404,
            task_id_exc_templ.detail,
        ),
    ],
    indirect=["mutated_task"],
)
@pytest.mark.asyncio
async def test_endpoint_delete_task_by_user(
    async_client: AsyncClient,
    mutated_task: dict,
    expected_code,
    expected_details,
):
    wrong_task = mutated_task.get("task_id_for_task")
    task = wrong_task if wrong_task else mutated_task.get("task").id
    response = await async_client.delete(
        url=f"{settings.api.task.prefix}/{task}/",
        headers=mutated_task.get("headers"),
    )
    assert response.status_code == expected_code
    if expected_details == task_id_exc_templ.detail:
        exc = rendering_exception_with_param(task_id_exc_templ, wrong_task)
        assert response.json().get("detail") == exc.detail
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
        ({"target": "headers_none"}, 401, token_invalid_exc.detail),
        (
            {"target": "user", "attrs": {"role": settings.roles.user}},
            403,
            no_priv_except.detail,
        ),
    ],
    indirect=["mutated_admin"],
)
@pytest.mark.asyncio
async def test_endpoint_delete_task_by_admin(
    async_client: AsyncClient,
    mutated_admin: dict,
    test_task: dict,
    expected_code,
    expected_details,
):
    response = await async_client.delete(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/",
        headers=mutated_admin.get("headers"),
    )
    assert response.status_code == expected_code
    assert response.json().get("detail") == expected_details
