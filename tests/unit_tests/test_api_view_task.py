import pytest
from api.views.task import (
    change_task_owner,
    delete_task,
    search_task_by_parameters,
    update_task,
)
from core.config import settings
from fastapi import HTTPException


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_id",
    [0, 1, 2],
)
async def test_search_task_by_parameters_success(mocker, user_mock, task_mock, task_id):
    session_mock = mocker.AsyncMock()
    expect_task = task_mock(task_id)
    cur_user = user_mock(0)
    mocker.patch(
        "api.views.task.crud.get_tasks_by_some_statement",
        new=mocker.AsyncMock(return_value=[expect_task]),
    )
    result = await search_task_by_parameters(
        session_mock,
        expect_task,
        cur_user,
    )
    assert result[0].id == expect_task.id


@pytest.mark.asyncio
async def test_search_task_by_parameters_bad_request(mocker, user_mock, task_mock):
    session_mock = mocker.AsyncMock()
    expect_task = task_mock(3)
    cur_user = user_mock(0)
    mocker.patch(
        "api.views.task.crud.get_tasks_by_some_statement",
        new=mocker.AsyncMock(return_value=[expect_task]),
    )
    with pytest.raises(HTTPException) as exc_info:
        await search_task_by_parameters(
            session_mock,
            expect_task,
            cur_user,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Status '{expect_task.status}' not exist"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cur_user_id",
    [0, 2],
)
async def test_change_task_owner_success(mocker, user_mock, task_mock, cur_user_id):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(cur_user_id)
    task_id = 1
    expect_task = task_mock(task_id)
    if cur_user.role != settings.roles.admin:
        expect_task.user_id = cur_user.id
    new_user = user_mock(1)
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    mocker.patch(
        "api.views.task.crud.change_task_user_by_user",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    result = await change_task_owner(session_mock, task_id, cur_user, new_user)
    assert result.id == expect_task.id


@pytest.mark.asyncio
async def test_change_task_owner_privileges_exc(mocker, user_mock, task_mock):
    session_mock = mocker.AsyncMock()
    task_id = 1
    expect_task = task_mock(task_id)
    new_user = user_mock(1)
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    with pytest.raises(HTTPException) as exc_info:
        await change_task_owner(session_mock, task_id, user_mock(1), new_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not enough privileges"


@pytest.mark.asyncio
async def test_change_task_owner_task_not_exist_exc(mocker, user_mock, task_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(0)
    task_id = 11
    expect_task = task_mock(task_id)
    new_user = user_mock(1)
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    with pytest.raises(HTTPException) as exc_info:
        await change_task_owner(session_mock, task_id, cur_user, new_user)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Task with id=[{task_id}] not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cur_user_id",
    [0, 2],
)
async def test_update_task_success(mocker, user_mock, task_mock, cur_user_id):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(cur_user_id)
    task_input = task_mock(0)
    task_id = 1
    expect_task = task_mock(task_id)
    if cur_user.role != settings.roles.admin:
        expect_task.user_id = cur_user.id
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    mocker.patch(
        "api.views.task.crud.update_task",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    result = await update_task(session_mock, task_input, task_id, cur_user)
    assert result.id == expect_task.id


@pytest.mark.asyncio
async def test_update_task_privileges_exc(mocker, user_mock, task_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(1)
    task_input = task_mock(0)
    task_id = 1
    expect_task = task_mock(task_id)
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    with pytest.raises(HTTPException) as exc_info:
        await update_task(session_mock, task_input, task_id, cur_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not enough privileges"


@pytest.mark.asyncio
async def test_update_task_task_not_exist_exc(mocker, user_mock, task_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(1)
    task_input = task_mock(0)
    task_id = 11
    expect_task = task_mock(task_id)
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=expect_task),
    )
    with pytest.raises(HTTPException) as exc_info:
        await update_task(session_mock, task_input, task_id, cur_user)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Task with id=[{task_id}] not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cur_user_id",
    [0, 2],
)
async def test_delete_task_success(mocker, user_mock, task_mock, cur_user_id):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(cur_user_id)
    task_id = 1
    task_to_delete = task_mock(task_id)
    if cur_user.role != settings.roles.admin:
        task_to_delete.user_id = cur_user.id
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=task_to_delete),
    )
    mocker.patch(
        "api.views.task.crud.delete_task",
    )
    result = await delete_task(session_mock, task_id, cur_user)
    assert result is None


@pytest.mark.asyncio
async def test_delete_task_privileges_exc(mocker, user_mock, task_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(1)
    task_id = 1
    task_to_delete = task_mock(task_id)
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=task_to_delete),
    )
    with pytest.raises(HTTPException) as exc_info:
        await delete_task(session_mock, task_id, cur_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not enough privileges"


@pytest.mark.asyncio
async def test_delete_task_task_not_exist_exc(mocker, user_mock, task_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(1)
    task_id = 11
    task_to_delete = task_mock(task_id)
    mocker.patch(
        "api.views.task.crud.get_task_by_id",
        new=mocker.AsyncMock(return_value=task_to_delete),
    )
    with pytest.raises(HTTPException) as exc_info:
        await delete_task(session_mock, task_id, cur_user)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Task with id=[{task_id}] not found"
