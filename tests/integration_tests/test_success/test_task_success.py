from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import UserSchmExtended
from core.config import settings
from api.schemas.task import TaskSchm
from core.crud import task as task_crud


@pytest.mark.asyncio
async def test_endpoint_get_all_tasks(
    async_client: AsyncClient,
    test_session: AsyncSession,
    admin_user: dict,
    test_task_a: dict,
    test_user_b: dict,
):
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/all/",
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 200
    tasks = await task_crud.get_all_tasks(test_session)
    expected = [TaskSchm.model_validate(t).model_dump(mode="json") for t in tasks]
    assert response.json() == expected


@pytest.mark.parametrize(
    "search_attr_list",
    [
        ("id",),
        ("name",),
        ("start_at",),
        ("end_at",),
        ("user_id",),
        ("status",),
        ("id", "status"),
        ("name", "end_at"),
        ("start_at", "user_id"),
        ("name", "end_at", "status"),
        ("start_at", "user_id", "id"),
        ("name", "end_at", "status", "start_at", "user_id", "id"),
    ],
)
@pytest.mark.asyncio
async def test_endpoint_search_task_by_parameters(
    async_client: AsyncClient,
    test_user_c: dict,
    test_multiple_tasks: dict,
    search_attr_list,
):
    task = test_multiple_tasks.get("task_list")[0]
    params = {}

    for key in search_attr_list:
        value = getattr(task, key)
        if value is None:
            pytest.skip(f"У задачи нет значения для поля {key}")

        if hasattr(value, "isoformat"):
            value = value.isoformat()

        params[key] = value
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/search/",
        params=params,
        headers=test_user_c.get("headers"),
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    for res in data:
        for key in search_attr_list:
            expected_val = params[key]
            actual_val = res[key]

            if key == "start_at":
                assert datetime.fromisoformat(actual_val) >= datetime.fromisoformat(
                    expected_val
                )
            elif key == "end_at":
                assert datetime.fromisoformat(actual_val) <= datetime.fromisoformat(
                    expected_val
                )
            else:
                assert actual_val == expected_val


@pytest.mark.asyncio
async def test_endpoint_get_task_by_user_id(
    async_client: AsyncClient,
    test_session: AsyncSession,
    admin_user: dict,
    test_task: dict,
):
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/by-user/{test_task.get("task").user_id}/",
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 200
    user = test_task.get("user")
    tasks = await task_crud.get_user_all_tasks(
        test_session, UserSchmExtended.model_validate(user)
    )
    expected = [TaskSchm.model_validate(t).model_dump(mode="json") for t in tasks]
    assert response.json() == expected


@pytest.mark.asyncio
async def test_endpoint_get_user_all_tasks(
    async_client: AsyncClient,
    test_multiple_tasks: dict,
):
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/",
        headers=test_multiple_tasks.get("headers"),
    )
    assert response.status_code == 200
    expected = [
        TaskSchm.model_validate(t).model_dump(mode="json")
        for t in test_multiple_tasks.get("task_list")
    ]
    assert response.json() == expected


@pytest.mark.asyncio
async def test_endpoint_get_task_by_task_id(
    async_client: AsyncClient,
    test_session: AsyncSession,
    admin_user: dict,
    test_task: dict,
):
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/",
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 200
    assert response.json().get("name") == test_task.get("task").name
    assert response.json().get("description") == test_task.get("task").description
    assert response.json().get("start_at") == test_task.get("task").start_at.strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    assert response.json().get("end_at") == test_task.get("task").end_at.strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    assert (
        response.json().get("scheduled_hours") == test_task.get("task").scheduled_hours
    )
    assert response.json().get("status") == test_task.get("task").status
    assert response.json().get("user_id") == test_task.get("task").user_id


@pytest.mark.asyncio
async def test_endpoint_create_task(
    async_client: AsyncClient,
    test_user: dict,
    test_task_to_create: dict,
):
    response = await async_client.post(
        url=f"{settings.api.task.prefix}/",
        headers=test_user.get("headers"),
        json=test_task_to_create,
    )
    assert response.status_code == 201
    assert response.json().get("name") == test_task_to_create.get("name")
    assert response.json().get("description") == test_task_to_create.get("description")
    assert datetime.fromisoformat(
        response.json().get("start_at")
    ) == datetime.fromisoformat(test_task_to_create.get("start_at"))
    assert datetime.fromisoformat(
        response.json().get("end_at")
    ) == datetime.fromisoformat(test_task_to_create.get("end_at"))
    assert response.json().get("scheduled_hours") == test_task_to_create.get(
        "scheduled_hours"
    )


@pytest.mark.asyncio
async def test_endpoint_change_task_owner_by_user(
    async_client: AsyncClient,
    test_task: dict,
    test_user_c: dict,
):
    new_user_id = test_user_c.get("user").id
    old_user_id = test_task.get("user").id
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/change_owner/",
        headers=test_task.get("headers"),
        params={"user_id": new_user_id},
    )
    assert response.status_code == 200
    assert response.json().get("name") == test_task.get("task").name
    assert response.json().get("id") == test_task.get("task").id
    assert response.json().get("user_id") == new_user_id
    assert response.json().get("user_id") != old_user_id


@pytest.mark.asyncio
async def test_endpoint_change_task_owner_by_admin(
    async_client: AsyncClient,
    admin_user: dict,
    test_task: dict,
    test_user_c: dict,
):
    new_user_id = test_user_c.get("user").id
    old_user_id = test_task.get("user").id
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/change_owner/",
        headers=admin_user.get("headers"),
        params={"user_id": new_user_id},
    )
    assert response.status_code == 200
    assert response.json().get("name") == test_task.get("task").name
    assert response.json().get("id") == test_task.get("task").id
    assert response.json().get("user_id") == new_user_id
    assert response.json().get("user_id") != old_user_id


@pytest.mark.asyncio
async def test_endpoint_update_task_by_user(
    async_client: AsyncClient,
    test_task: dict,
):
    update_scenario = test_task.get("update_scenarios").get("user")
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/",
        headers=test_task.get("headers"),
        json=update_scenario,
    )
    assert response.status_code == 200

    for attr, value in update_scenario.items():
        if attr in ["start_at", "end_at"]:
            assert datetime.fromisoformat(
                response.json().get(attr)
            ) == datetime.fromisoformat(value)
        else:
            assert response.json().get(attr) == value


@pytest.mark.asyncio
async def test_endpoint_update_task_by_admin(
    async_client: AsyncClient,
    admin_user: dict,
    test_task: dict,
):
    update_scenario = test_task.get("update_scenarios").get("admin")
    response = await async_client.patch(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/",
        headers=admin_user.get("headers"),
        json=update_scenario,
    )
    assert response.status_code == 200

    for attr, value in update_scenario.items():
        if attr in ["start_at", "end_at"]:
            assert datetime.fromisoformat(
                response.json().get(attr)
            ) == datetime.fromisoformat(value)
        else:
            assert response.json().get(attr) == value


@pytest.mark.asyncio
async def test_endpoint_delete_task_by_user(
    async_client: AsyncClient,
    test_task: dict,
):
    response = await async_client.delete(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/",
        headers=test_task.get("headers"),
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_endpoint_delete_task_by_admin(
    async_client: AsyncClient,
    admin_user: dict,
    test_task: dict,
):
    response = await async_client.delete(
        url=f"{settings.api.task.prefix}/{test_task.get("task").id}/",
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 204
