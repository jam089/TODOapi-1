import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User

from tests.helpers import authentication

FLG_STATEMENTS = [
    "json_none",
    "user_already_exist",
]
VALUE_STATEMENTS = [
    "refresh_token",
    "password",
    "wrong_user_id_to_request",
    "wrong_role_to_request",
    "wrong_password",
    "wrong_username",
]


async def mutated(
    request,
    test_session: AsyncSession,
    async_client: AsyncClient,
    user: dict,
):
    """
    Examples:
    {"target": "access_token", "value": "wrong_token"}
    {"target": "user", "attrs": {"active": False}}
    """

    wrong_param = request.param or {}
    target = wrong_param.get("target")

    if target == "user":
        user_obj: User = user.get("user")
        attrs: dict = wrong_param.get("attrs")
        for attr, value in attrs.items():
            setattr(user_obj, attr, value)
        await test_session.commit()
        await test_session.refresh(user_obj)
        if "role" in attrs.keys():
            new_auth_info = await authentication(
                async_client, user_obj, user.get("password")
            )
            user.update(new_auth_info)

    elif target in VALUE_STATEMENTS:
        value = wrong_param.get("value")
        user[target] = value
        if target == "access_token":
            user["headers"] = {"Authorization": f"Bearer {value}"}

    elif target == "headers_none":
        user["headers"] = None

    elif target in FLG_STATEMENTS:
        user[target] = True

    return user


@pytest.fixture
async def mutated_user(request, test_session, auth_client, test_user):
    return await mutated(request, test_session, auth_client, test_user)


@pytest.fixture
async def mutated_admin(request, test_session, auth_client, admin_user):
    return await mutated(request, test_session, auth_client, admin_user)
