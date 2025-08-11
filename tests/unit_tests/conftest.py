from typing import Any

import pytest
from datetime import datetime

from core.models import User, Task
from core.config import settings


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
        User(
            id=0,
            username="test_user_0",
            name="Test User 0",
            role=settings.roles.user,
            active=True,
            created_at=datetime.now(),
            password="test0",
        ),
        User(
            id=1,
            username="test_user_1",
            name="Test User 1",
            role=settings.roles.user,
            active=False,
            created_at=datetime.now(),
            password="test1",
        ),
        User(
            id=2,
            username="test_admin_2",
            name="Test Admin 2",
            role=settings.roles.admin,
            active=True,
            created_at=datetime.now(),
            password="test2",
        ),
    ]

    def _get_user(identifier: Any) -> User | None:
        if isinstance(identifier, int):
            try:
                return user_list[identifier]
            except IndexError:
                return None
        elif isinstance(identifier, str):
            return next(
                (user for user in user_list if user.username == identifier), None
            )
        else:
            raise ValueError("Identifier must be an int or str")

    return _get_user


@pytest.fixture(scope="package")
def task_mock():
    task_list = [
        Task(id=0, name="Test Task 0", status=settings.tstat.pld),
        Task(id=1, name="Test Task 1"),
        Task(id=2, name="Test Task 2", status=settings.tstat.atw),
        Task(id=3, name="Test Task 3", status="Very_needed"),
    ]

    def _create_task(task_id):
        try:
            return task_list[task_id]
        except IndexError:
            return None

    return _create_task
