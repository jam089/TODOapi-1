import pytest

from core.crud.user import _create_user_helper


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data",
    [
        {
            "username": "TestUser",
            "name": "User Name",
            "b_date": "",
            "password": "testpass1",
        },
        {
            "username": "TestAdmin",
            "name": "Admin Name",
            "b_date": "",
            "password": "testpass2",
            "id": "-10",
            "active": True,
        },
    ],
)
async def test_create_user_crud(mocker, user_data):
    def refresh_side_effect(user):
        user.id = 1

    session_mock = mocker.AsyncMock()
    session_mock.add = mocker.MagicMock()
    session_mock.commit = mocker.AsyncMock()
    session_mock.refresh = mocker.AsyncMock(side_effect=refresh_side_effect)

    user = await _create_user_helper(session_mock, user_data)

    session_mock.add.assert_called_once_with(user)
    session_mock.commit.assert_awaited_once()
    session_mock.refresh.assert_awaited_once_with(user)
    assert user.id is not None
    assert user.username == user_data["username"]
    assert user.password != user_data["password"]
    assert user.password.startswith("$2b$")
