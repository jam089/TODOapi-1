import pytest
from fastapi import HTTPException
from jwt import InvalidTokenError

from api.auth.validation import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
    validate_token_type,
    get_user_from_payload,
    get_currant_token_payload_of_token_type,
    get_auth_user_from_token_of_type,
    get_auth_user_from_db,
)


def make_get_user_by_mock(user_mock):
    async def get_user_by_id_mock(session, *args, **kwargs):
        user_id = args[0] if args else kwargs.get("username")
        return user_mock(user_id)

    return get_user_by_id_mock


def test_validate_token_type():
    payload = {"type": ACCESS_TOKEN_TYPE}
    assert validate_token_type(payload, ACCESS_TOKEN_TYPE)


def test_validate_token_type_invalid():
    payload = {"type": REFRESH_TOKEN_TYPE}
    with pytest.raises(HTTPException) as exc_info:
        validate_token_type(payload, ACCESS_TOKEN_TYPE)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_get_user_from_payload_valid_user(mocker, user_mock):
    get_user_by_id_mock = make_get_user_by_mock(user_mock)
    mocker.patch(
        "api.auth.validation.get_user_by_id",
        new=get_user_by_id_mock,
    )
    session_mock = mocker.AsyncMock()
    payload = {"sub": user_mock(0).id}
    user = await get_user_from_payload(session_mock, payload)
    assert user.id == payload.get("sub")
    assert user.active


@pytest.mark.asyncio
async def test_get_user_from_payload_inactive_user(mocker, user_mock):
    get_user_by_id_mock = make_get_user_by_mock(user_mock)
    mocker.patch(
        "api.auth.validation.get_user_by_id",
        new=get_user_by_id_mock,
    )
    session_mock = mocker.AsyncMock()
    payload = {"sub": user_mock(1).id}
    with pytest.raises(HTTPException) as exc_info:
        await get_user_from_payload(session_mock, payload)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User is inactive"


@pytest.mark.asyncio
async def test_get_user_from_payload_no_user(mocker, user_mock):
    get_user_by_id_mock = make_get_user_by_mock(user_mock)
    mocker.patch(
        "api.auth.validation.get_user_by_id",
        new=get_user_by_id_mock,
    )
    session_mock = mocker.AsyncMock()
    payload = {"sub": 3}
    with pytest.raises(HTTPException) as exc_info:
        await get_user_from_payload(session_mock, payload)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_get_currant_token_payload_of_token_type_valid_token(mocker):
    mocker.patch(
        "api.auth.validation.decode_jwt",
        return_value="valid_token",
    )
    get_current_token_payload = get_currant_token_payload_of_token_type("valid_token")
    payload = get_current_token_payload("valid_token")
    assert payload == "valid_token"


def test_get_currant_token_payload_of_token_type_invalid_token(mocker):
    mocker.patch(
        "api.auth.validation.decode_jwt",
        side_effect=InvalidTokenError(),
    )
    get_current_token_payload = get_currant_token_payload_of_token_type("invalid_token")
    with pytest.raises(HTTPException) as exc_info:
        get_current_token_payload("invalid_token")
    assert exc_info.value.detail == "Invalid token"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_role_to_check",
    ["User", None],
)
async def test_get_auth_user_from_token_of_type_with_privileges(
    mocker,
    user_mock,
    user_role_to_check,
):
    get_auth_user_from_token = get_auth_user_from_token_of_type(
        ACCESS_TOKEN_TYPE, user_role_to_check
    )
    payload = {
        "sub": 0,
        TOKEN_TYPE_FIELD: ACCESS_TOKEN_TYPE,
        "role": "User",
        "active": True,
    }
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.auth.validation.get_user_by_id",
        new=make_get_user_by_mock(user_mock),
    )

    user = await get_auth_user_from_token(session_mock, payload)
    assert user.id == payload["sub"]


@pytest.mark.asyncio
async def test_get_auth_user_from_token_of_type_without_privileges(
    mocker,
    user_mock,
):
    get_auth_user_from_token = get_auth_user_from_token_of_type(
        ACCESS_TOKEN_TYPE, "Admin"
    )
    payload = {
        "sub": 0,
        TOKEN_TYPE_FIELD: ACCESS_TOKEN_TYPE,
        "role": "User",
        "active": True,
    }
    session_mock = mocker.AsyncMock()
    mocker.patch(
        "api.auth.validation.get_user_by_id",
        new=make_get_user_by_mock(user_mock),
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_auth_user_from_token(session_mock, payload)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not enough privileges"


@pytest.mark.asyncio
async def test_get_auth_user_from_db_success(mocker, user_mock):
    username = "test_user_0"
    password = "test1"
    session_mock = mocker.AsyncMock()
    get_user_by_id_mock = make_get_user_by_mock(user_mock)
    mocker.patch(
        "api.auth.validation.get_user_by_username",
        new=get_user_by_id_mock,
    )
    mocker.patch(
        "api.auth.validation.check_password",
        return_value=True,
    )

    user = await get_auth_user_from_db(
        session=session_mock,
        username=username,
        password=password,
    )
    assert user.username == username


@pytest.mark.asyncio
async def test_get_auth_user_from_db_no_user(mocker, user_mock):
    username = "test_no_user"
    password = "test1"
    session_mock = mocker.AsyncMock()
    get_user_by_id_mock = make_get_user_by_mock(user_mock)
    mocker.patch(
        "api.auth.validation.get_user_by_username",
        new=get_user_by_id_mock,
    )
    mocker.patch(
        "api.auth.validation.check_password",
        return_value=True,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_auth_user_from_db(
            session=session_mock,
            username=username,
            password=password,
        )
    assert exc_info.value.detail == "Invalid login or password"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_auth_user_from_db_wrong_password(mocker, user_mock):
    username = "test_user_0"
    password = "test1"
    session_mock = mocker.AsyncMock()
    get_user_by_id_mock = make_get_user_by_mock(user_mock)
    mocker.patch(
        "api.auth.validation.get_user_by_username",
        new=get_user_by_id_mock,
    )
    mocker.patch(
        "api.auth.validation.check_password",
        return_value=False,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_auth_user_from_db(
            session=session_mock,
            username=username,
            password=password,
        )
    assert exc_info.value.detail == "Invalid login or password"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_auth_user_from_db_inactive_user(mocker, user_mock):
    username = "test_user_1"
    password = "test1"
    session_mock = mocker.AsyncMock()
    get_user_by_id_mock = make_get_user_by_mock(user_mock)
    mocker.patch(
        "api.auth.validation.get_user_by_username",
        new=get_user_by_id_mock,
    )
    mocker.patch(
        "api.auth.validation.check_password",
        return_value=True,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_auth_user_from_db(
            session=session_mock,
            username=username,
            password=password,
        )
    assert exc_info.value.detail == "User is inactive"
    assert exc_info.value.status_code == 401
