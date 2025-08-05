import pytest
from unittest.mock import AsyncMock

from core.models import User
from core.utils.on_startup_scripts import check_and_create_superuser


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "admin_id, username, password, admin_exists, expected",
    [
        (-2, "admin", "admin", False, "admin created"),
        (-2, "admin", "admin", True, "admin is exist"),
        (None, None, None, False, "admin created"),
        (None, None, None, True, "admin is exist"),
    ],
)
async def test_check_and_create_superuser(
    mocker,
    admin_id,
    username,
    password,
    admin_exists,
    expected,
):
    session_mock = mocker.AsyncMock()

    async def mocked_get_user_by_id(session, user_id):
        if admin_exists:
            return User(id=admin_id, username=username)
        return None

    mocker.patch(
        "core.utils.on_startup_scripts.get_user_by_id",
        new_callable=AsyncMock,
        side_effect=mocked_get_user_by_id,
    )
    mocker.patch(
        "core.utils.on_startup_scripts.create_user",
        new_callable=AsyncMock,
    )
    mocker.patch(
        "core.utils.on_startup_scripts.update_role",
        new_callable=AsyncMock,
    )
    result = (
        await check_and_create_superuser(
            session_mock,
            admin_id,
            username,
            password,
        )
        if admin_id
        else await check_and_create_superuser(session_mock)
    )
    assert result == expected
