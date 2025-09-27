import pytest
from core.config import settings
from core.utils.jwt import hash_password
from factory.faker import faker
from integration_tests.create_update_scenarios import (
    create_tasks,
    create_users,
    update_task_scenarios,
    update_user_scenarios,
)
from integration_tests.factories import TaskFactory

from tests.helpers import authentication
from tests.integration_tests.factories import UserFactory, create


@pytest.fixture
async def test_user_a(auth_client):
    password = faker.Faker().password()
    user = await create(UserFactory, password=hash_password(password).decode())
    auth_response = await authentication(auth_client, user, password)
    return {
        "user": user,
        "password": password,
        "update_user_scenarios": update_user_scenarios.get("test_user_a"),
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
        "update_user_scenarios": update_user_scenarios.get("test_user_b"),
        **auth_response,
    }


@pytest.fixture
async def test_user_c(auth_client):
    password = faker.Faker().password()
    user = await create(UserFactory, password=hash_password(password).decode())
    auth_response = await authentication(auth_client, user, password)
    return {
        "user": user,
        "password": password,
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
    user = test_user_a.get("user")
    task = await create(TaskFactory, user=user)
    return {
        "task": task,
        "user": user,
        "update_scenarios": update_task_scenarios.get("test_task_a"),
        **test_user_a,
    }


@pytest.fixture
async def test_task_b(test_user_b):
    user = test_user_b.get("user")
    task = await create(TaskFactory, user=user)
    return {
        "task": task,
        "user": user,
        "update_scenarios": update_task_scenarios.get("test_task_b"),
        **test_user_b,
    }


@pytest.fixture(params=["test_task_a", "test_task_b"])
async def test_task(request, test_task_a, test_task_b):
    match request.param:
        case "test_task_a":
            return test_task_a
        case "test_task_b":
            return test_task_b
        case _:
            return None


@pytest.fixture
async def test_multiple_tasks_a(test_user_a):
    task_list = [
        await create(TaskFactory, user=test_user_a.get("user")) for _ in range(4)
    ]
    return {
        "task_list": task_list,
        "user": test_user_a.get("user"),
        **test_user_a,
    }


@pytest.fixture
async def test_multiple_tasks_b(test_user_b):
    task_list = [
        await create(TaskFactory, user=test_user_b.get("user")) for _ in range(4)
    ]
    return {
        "task_list": task_list,
        "user": test_user_b.get("user"),
        **test_user_b,
    }


@pytest.fixture(params=["test_multiple_tasks_a", "test_multiple_tasks_b"])
async def test_multiple_tasks(request, test_multiple_tasks_a, test_multiple_tasks_b):
    match request.param:
        case "test_multiple_tasks_a":
            return test_multiple_tasks_a
        case "test_multiple_tasks_b":
            return test_multiple_tasks_b
        case _:
            return None


@pytest.fixture(params=["task_1", "task_2"])
async def test_task_to_create(request):
    return create_tasks.get(request.param)
