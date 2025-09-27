from core.config import settings
from factory.faker import faker

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

update_user_scenarios = {
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

create_tasks = {
    "task_1": {
        "name": "Test Task 1",
        "description": "very needed task",
        "start_at": "2000-09-25T09:21:45.656Z",
        "end_at": "2020-09-25T09:21:45.656Z",
        "scheduled_hours": 999,
    },
    "task_2": {
        "name": "Test Task 2",
        "description": "not very needed task",
        "start_at": "1987-09-25T09:21:45.656Z",
        "end_at": "2024-09-25T09:21:45.656Z",
        "scheduled_hours": 9,
    },
}

update_task_scenarios = {
    "test_task_a": {
        "admin": {
            "name": "test_update_by_admin_1",
            "description": "test_update_by_admin_1",
            "start_at": "2025-09-25T10:23:14.232Z",
            "end_at": "2025-09-25T10:23:14.232Z",
            "scheduled_hours": 1,
            "status": settings.tstat.atw,
        },
        "user": {
            "name": "test_update_1",
            "description": "test_update_1",
        },
    },
    "test_task_b": {
        "admin": {
            "description": "test_update_by_admin_2",
            "scheduled_hours": 2,
            "status": settings.tstat.cmp,
        },
        "user": {
            "name": "test_update_2",
            "start_at": "2001-09-25T10:23:14.232Z",
            "end_at": "2002-09-25T10:23:14.232Z",
        },
    },
}
