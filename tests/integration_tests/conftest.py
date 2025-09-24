from factory.faker import faker
import pytest

from core.config import settings
from core.utils.jwt import hash_password
from integration_tests.factories import TaskFactory
from tests.integration_tests.database import (
    override_dispose,
    override_session_getter,
    pytest_addoption,
    pytest_configure,
    prepare_db,
    test_session,
    async_client,
    auth_client,
)
from tests.integration_tests.factories import UserFactory, create
from tests.helpers import authentication


create_users = {
    "user_1": {
        "username": faker.Faker().user_name(),
        "password": faker.Faker().password(),
        "name": faker.Faker().name(),
        "b_date": faker.Faker().date_of_birth().strftime("%Y-%m-%d"),
    },
    "user_2": {
        "username": faker.Faker().user_name(),
        "password": faker.Faker().password(),
    },
}

update_scenarios = {
    "test_user_a": {
        "admin": {
            "username": "jackson",
            "name": "Jack N",
        },
        "user": {
            "username": "jack_nicholson",
            "name": "Jack Nicholson",
            "b_date": "2000-12-01",
            "active": True,
        },
    },
    "test_user_b": {
        "admin": {
            "username": "john_doe2",
        },
        "user": {
            "username": "johnny_d",
            "name": "Johnny",
        },
    },
}


@pytest.fixture
async def test_user_a(auth_client):
    password = faker.Faker().password()
    user = await create(UserFactory, password=hash_password(password).decode())
    auth_response = await authentication(auth_client, user, password)
    return {
        "user": user,
        "password": password,
        "update_scenarios": update_scenarios.get("test_user_a"),
        **auth_response,
    }


@pytest.fixture
async def test_user_b(auth_client):
    password = faker.Faker().password()
    user = await create(UserFactory, password=hash_password(password).decode())
    auth_response = await authentication(auth_client, user, password)
    return {
        "user": user,
        "password": password,
        "update_scenarios": update_scenarios.get("test_user_b"),
        **auth_response,
    }


@pytest.fixture
async def admin_user(auth_client):
    password = faker.Faker().password()
    user = await create(
        UserFactory,
        name=None,
        b_date=None,
        role=settings.roles.admin,
        password=hash_password(password).decode(),
    )
    auth_response = await authentication(auth_client, user, password)
    return {
        "user": user,
        "password": password,
        **auth_response,
    }


@pytest.fixture(params=["test_user_a", "test_user_b"])
async def test_user(request, test_user_a, test_user_b):
    match request.param:
        case "test_user_a":
            return test_user_a
        case "test_user_b":
            return test_user_b
        case _:
            return None


@pytest.fixture(params=["user_1", "user_2"])
async def test_user_to_create(request):
    return create_users.get(request.param)


@pytest.fixture
async def test_task_a(test_user_a):
    task = await create(TaskFactory, user=test_user_a.get("user"))
    return task


@pytest.fixture
async def test_task_b(test_user_b):
    task = await create(TaskFactory, user=test_user_b.get("user"))
    return task
