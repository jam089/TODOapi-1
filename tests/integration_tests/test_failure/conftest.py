import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User

from tests.helpers import authentication


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

    elif target == "access_token":
        value = wrong_param.get("value")
        user["access_token"] = value
        user["headers"] = {"Authorization": f"Bearer {value}"}

    elif target == "refresh_token":
        value = wrong_param.get("value")
        user["refresh_token"] = value

    elif target == "password":
        value = wrong_param.get("value")
        user["password"] = value

    elif target == "headers_none":
        user["headers"] = None

    elif target == "wrong_user_id_to_request":
        value = wrong_param.get("value")
        user["wrong_user_id_to_request"] = value

    elif target == "json_none":
        user["json_none"] = True

    elif target == "user_already_exist":
        user["user_already_exist"] = True

    elif target == "wrong_role_to_request":
        value = wrong_param.get("value")
        user["wrong_role_to_request"] = value

    return user


@pytest.fixture
async def mutated_user(request, test_session, auth_client, test_user):
    return await mutated(request, test_session, auth_client, test_user)


@pytest.fixture
async def mutated_admin(request, test_session, auth_client, admin_user):
    return await mutated(request, test_session, auth_client, admin_user)
