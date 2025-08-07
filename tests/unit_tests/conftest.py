import pytest

from core.models import User, Task


@pytest.fixture(scope="package")
def jwt_payload_example():
    payload = {
        "type": "access",
        "iss": "john@malkovich.com",
        "sub": 7,
        "username": "john",
        "jti": "15937a7e-2a4f-41aa-9267-ee2ec264069b",
        "name": "John Malkovich",
        "logged_in_at": 1722351564.249006,
        "role": "User",
    }
    return payload


@pytest.fixture(scope="package")
def user_mock():
    user_list = [
        User(id=0, name="Test User 1"),
        User(id=1, name="Test User 2"),
    ]

    def _create_user(user_id):
        try:
            return user_list[user_id]
        except IndexError:
            return None

    return _create_user


@pytest.fixture(scope="package")
def task_mock():
    task_list = [
        Task(id=0, name="Test Task 1"),
        Task(id=1, name="Test Task 2"),
    ]

    def _create_task(task_id):
        try:
            return task_list[task_id]
        except IndexError:
            return None

    return _create_task
