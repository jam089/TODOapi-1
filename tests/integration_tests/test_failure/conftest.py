import pytest
from core.models import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import authentication

FLG_STATEMENTS = [
    "json_none",
    "user_already_exist",
]
VALUE_STATEMENTS = [
    "access_token",
    "refresh_token",
    "password",
    "wrong_user_id_to_request",
    "wrong_role_to_request",
    "wrong_password",
    "wrong_username",
    "user_id_for_task",
    "task_id_for_task",
    "wrong_json",
    "wrong_status",
]


async def mutated(
    request,
    test_session: AsyncSession,
    async_client: AsyncClient,
    obj_dict: dict,
):
    """
    Examples:
    {"target": "access_token", "value": "wrong_token"}
    {"target": "user", "attrs": {"active": False}}
    """

    wrong_param = request.param or {}
    target = wrong_param.get("target")

    if target == "user":
        user_obj: User = obj_dict.get("user")
        user_obj = await test_session.merge(user_obj)
        attrs: dict = wrong_param.get("attrs")
        await test_session.refresh(user_obj)
        for attr, value in attrs.items():
            setattr(user_obj, attr, value)
        await test_session.commit()
        await test_session.refresh(user_obj)
        if "role" in attrs:
            new_auth_info = await authentication(
                async_client, user_obj, obj_dict.get("password")
            )
            obj_dict.update(new_auth_info)

    elif target in VALUE_STATEMENTS:
        value = wrong_param.get("value")
        obj_dict[target] = value
        if target == "access_token":
            obj_dict["headers"] = {"Authorization": f"Bearer {value}"}

    elif target == "headers_none":
        obj_dict["headers"] = None

    elif target in FLG_STATEMENTS:
        obj_dict[target] = True

    return obj_dict


@pytest.fixture
async def mutated_user(request, test_session, auth_client, test_user):
    return await mutated(request, test_session, auth_client, test_user)


@pytest.fixture
async def mutated_admin(request, test_session, auth_client, admin_user):
    return await mutated(request, test_session, auth_client, admin_user)


@pytest.fixture
async def mutated_task(request, test_session, auth_client, test_task):
    return await mutated(request, test_session, auth_client, test_task)


@pytest.fixture
async def mutated_multiple_task(
    request, test_session, auth_client, test_multiple_tasks
):
    return await mutated(request, test_session, auth_client, test_multiple_tasks)
