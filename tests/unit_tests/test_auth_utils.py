import pytest
from unittest.mock import Mock

from api.auth.utils import create_token, create_access_token, create_refresh_token


@pytest.mark.parametrize(
    "response",
    [None, Mock()],
)
def test_create_token(mocker, response):
    encode_mock = mocker.patch("api.auth.utils.encode_jwt", return_value="test_token")

    payload = {"sub": 1}
    token = create_token(
        token_type="access",
        payload=payload,
        expire_minutes=15,
        response=response,
    )
    expected_payload = {
        "type": "access",
        "sub": 1,
    }

    encode_mock.assert_called_once_with(
        payload=expected_payload,
        expire_minutes=15,
        expire_timedelta=None,
    )
    assert isinstance(token, str)
    assert token == "test_token"
