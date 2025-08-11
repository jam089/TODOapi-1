import pytest
from fastapi import HTTPException

from api.schemas.user import UserRoleChangeSchm
from api.views.user import (
    get_user_by_username,
    get_all_user_and_by_id,
    create_user,
    change_role,
    update_user,
    update_yourself,
)
from core.config import settings


@pytest.mark.asyncio
async def test_get_user_by_username_success_get_user(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    expected_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        mocker.AsyncMock(return_value=expected_user),
    )
    user_from_endpoint = await get_user_by_username(
        session_mock,
        expected_user.username,
    )
    assert user_from_endpoint.id == expected_user.id


@pytest.mark.asyncio
async def test_get_user_by_username_get_user_exception(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    expected_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        mocker.AsyncMock(return_value=None),
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_user_by_username(
            session_mock,
            expected_user.username,
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"User {expected_user.username} not exist"


@pytest.mark.asyncio
async def test_get_all_user_and_by_id_get_all_users(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = mocker.Mock()
    expected_users = [user_mock(i) for i in range(2)]
    mocker.patch(
        "api.views.user.user.get_all_users",
        new=mocker.AsyncMock(return_value=expected_users),
    )
    result = await get_all_user_and_by_id(session_mock, cur_user)
    result = [result[i].username for i in range(len(result))]
    expected_users = [expected_users[i].username for i in range(len(expected_users))]

    assert result == expected_users


@pytest.mark.asyncio
async def test_get_all_user_and_by_id_success_getting_user(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(2)
    expected_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_id",
        new=mocker.AsyncMock(return_value=expected_user),
    )

    result = await get_all_user_and_by_id(session_mock, cur_user, 0)

    assert result.username == expected_user.username


@pytest.mark.asyncio
async def test_get_all_user_and_by_id_no_user_with_id_exc(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(2)
    expect_user_id = 4
    mocker.patch(
        "api.views.user.user.get_user_by_id",
        new=mocker.AsyncMock(return_value=user_mock(expect_user_id)),
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_all_user_and_by_id(session_mock, cur_user, expect_user_id)

    assert exc_info.value.detail == f"User with id=[{expect_user_id}] not found"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_all_user_and_by_id_no_privileges_exc(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_id",
        new=mocker.AsyncMock(return_value=user_mock(0)),
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_all_user_and_by_id(session_mock, cur_user, 0)

    assert exc_info.value.detail == "Not enough privileges"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_create_user_success(mocker, user_mock):
    expect_user = user_mock(0)
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        mocker.AsyncMock(return_value=None),
    )
    mocker.patch(
        "api.views.user.user.create_user",
        mocker.AsyncMock(return_value=expect_user),
    )
    result = await create_user(session_mock, expect_user)
    assert result.username == expect_user.username
    assert result.id == expect_user.id


@pytest.mark.asyncio
async def test_create_user_user_already_exist_exc(mocker, user_mock):
    expect_user = user_mock(0)
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        mocker.AsyncMock(return_value=expect_user),
    )
    with pytest.raises(HTTPException) as exc_info:
        await create_user(session_mock, expect_user)
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == f"Username '{expect_user.username}' already exist"


@pytest.mark.asyncio
async def test_create_user_success(mocker, user_mock):
    cur_user = user_mock(2)
    expect_user = user_mock(0)
    session_mock = mocker.AsyncMock()
    role_for_update = UserRoleChangeSchm(role=settings.roles.admin)
    mocker.patch(
        "api.views.user.user.update_role",
        mocker.AsyncMock(return_value=expect_user),
    )
    result = await change_role(role_for_update, session_mock, expect_user, cur_user)
    assert result.username == expect_user.username
    assert result.id == expect_user.id


@pytest.mark.asyncio
async def test_create_user_role_not_exist_exc(mocker, user_mock):
    cur_user = user_mock(2)
    expect_user = user_mock(0)
    session_mock = mocker.AsyncMock()
    role_for_update = UserRoleChangeSchm(role="God")
    mocker.patch(
        "api.views.user.user.update_role",
        mocker.AsyncMock(return_value=expect_user),
    )
    with pytest.raises(HTTPException) as exc_info:
        await change_role(role_for_update, session_mock, expect_user, cur_user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Role '{role_for_update.role}' not exist"


@pytest.mark.asyncio
async def test_update_user_success(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(2)
    user_input = user_mock(1)
    expect_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        new=mocker.AsyncMock(return_value=None),
    )
    mocker.patch(
        "api.views.user.user.update_user",
        new=mocker.AsyncMock(return_value=expect_user),
    )

    result = await update_user(user_input, session_mock, expect_user, cur_user)
    assert result.username == expect_user.username
    assert result.id == expect_user.id


@pytest.mark.asyncio
async def test_update_user_username_already_exist_exc(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(2)
    user_input = user_mock(1)
    expect_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        new=mocker.AsyncMock(return_value=True),
    )
    mocker.patch(
        "api.views.user.user.update_user",
        new=mocker.AsyncMock(return_value=expect_user),
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_user(user_input, session_mock, expect_user, cur_user)
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == f"Username '{user_input.username}' already exist"


@pytest.mark.asyncio
async def test_update_yourself_success(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(2)
    user_input = user_mock(1)
    expect_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        new=mocker.AsyncMock(return_value=None),
    )
    mocker.patch(
        "api.views.user.user.update_user",
        new=mocker.AsyncMock(return_value=expect_user),
    )

    result = await update_yourself(user_input, session_mock, cur_user)
    assert result.username == expect_user.username
    assert result.id == expect_user.id


@pytest.mark.asyncio
async def test_update_yourself_username_already_exist_exc(mocker, user_mock):
    session_mock = mocker.AsyncMock()
    cur_user = user_mock(2)
    user_input = user_mock(1)
    expect_user = user_mock(0)
    mocker.patch(
        "api.views.user.user.get_user_by_username",
        new=mocker.AsyncMock(return_value=True),
    )
    mocker.patch(
        "api.views.user.user.update_user",
        new=mocker.AsyncMock(return_value=expect_user),
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_yourself(user_input, session_mock, cur_user)
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == f"Username '{user_input.username}' already exist"
