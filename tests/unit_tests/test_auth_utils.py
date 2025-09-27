import time
import uuid
from unittest.mock import Mock

import pytest
from api.auth.utils import (
    ACCESS_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    create_token,
    get_token_of_type,
)


@pytest.mark.parametrize(
    "response",
    [None, Mock()],
)
def test_create_token(mocker, response):
    encode_mock = mocker.patch("api.auth.utils.encode_jwt", return_value="test_token")

    payload = {"sub": 1}
    token = create_token(
        token_type=ACCESS_TOKEN_TYPE,
        payload=payload,
        expire_minutes=15,
        response=response,
    )
    expected_payload = {
        "type": ACCESS_TOKEN_TYPE,
        "sub": 1,
    }

    encode_mock.assert_called_once_with(
        payload=expected_payload,
        expire_minutes=15,
        expire_timedelta=None,
    )
    assert isinstance(token, str)
    assert token == "test_token"


def test_create_access_token(mocker, user_mock):
    user = user_mock(1)
    response_mock = mocker.Mock()
    expected_keys = {"iss", "sub", "username", "jti", "name", "logged_in_at", "role"}

    create_token_mock = mocker.patch(
        "api.auth.utils.create_token",
        return_value="test_access_token",
    )
    create_access_token(user, response=response_mock)
    args, kwargs = create_token_mock.call_args
    payload = kwargs["payload"]

    assert set(payload.keys()) == expected_keys
    assert payload["sub"] == user.id
    assert payload["username"] == user.username
    assert payload["role"] == user.role
    assert payload["name"] == user.name
    uuid_obj = uuid.UUID(payload["jti"], version=4)
    assert isinstance(uuid_obj, uuid.UUID)
    now_ts = time.time()
    assert isinstance(payload["logged_in_at"], float)
    assert abs(payload["logged_in_at"] - now_ts) <= 2


def test_create_refresh_token(mocker, user_mock):
    user = user_mock(1)
    response_mock = mocker.Mock()
    expected_keys = {"sub"}

    create_token_mock = mocker.patch(
        "api.auth.utils.create_token",
        return_value="test_refresh_token",
    )
    create_refresh_token(user, response=response_mock)
    args, kwargs = create_token_mock.call_args
    payload = kwargs["payload"]

    assert "expire_timedelta" in kwargs
    assert set(payload.keys()) == expected_keys
    assert payload["sub"] == user.id


@pytest.mark.parametrize(
    "token_from_oauth2, expected",
    [
        (None, ACCESS_TOKEN_TYPE),
        ("token_from_oauth2", "token_from_oauth2"),
    ],
)
def test_get_token_of_type(mocker, token_from_oauth2, expected):
    request_mock = mocker.MagicMock()
    request_mock.cookies.get.return_value = ACCESS_TOKEN_TYPE

    get_token = get_token_of_type(ACCESS_TOKEN_TYPE)
    token = get_token(request_mock, token_from_oauth2)
    assert token == expected
