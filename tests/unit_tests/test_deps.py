import pytest
from api.deps import get_task, get_user
from fastapi import HTTPException


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id",
    [0, 1],
)
async def test_get_user_success(mocker, user_id, user_mock):
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.deps.user_crud.get_user_by_id",
        return_value=user_mock(user_id),
    )

    result = await get_user(session_mock, user_id)
    assert result.id == user_id


@pytest.mark.asyncio
async def test_get_user_not_found(mocker, user_mock):
    user_id = 3
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.deps.user_crud.get_user_by_id",
        return_value=user_mock(user_id),
    )
    with pytest.raises(HTTPException) as exc:
        await get_user(session_mock, user_id)
    assert exc.value.status_code == 404
    assert exc.value.detail == "User with id=[3] not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_id",
    [0, 1],
)
async def test_get_task_success(mocker, task_id, task_mock):
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.deps.task_crud.get_task_by_id",
        return_value=task_mock(task_id),
    )

    result = await get_task(session_mock, task_id)
    assert result.id == task_id


@pytest.mark.asyncio
async def test_get_task_not_found(mocker, task_mock):
    task_id = 10
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.deps.task_crud.get_task_by_id",
        return_value=task_mock(task_id),
    )
    with pytest.raises(HTTPException) as exc:
        await get_task(session_mock, task_id)
    assert exc.value.status_code == 404
    assert exc.value.detail == f"Task with id=[{task_id}] not found"
