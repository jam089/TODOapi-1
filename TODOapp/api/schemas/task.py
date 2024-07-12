from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseTask(BaseModel):
    pass


class CreateTask(BaseTask):
    name: str
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    scheduled_hours: int
    user_id: int


class UpdateTask(BaseTask):
    name: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    scheduled_hours: int | None
    status: str | None = None


class ChangeTaskUser(BaseTask):
    user_id: int


class Task(CreateTask):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
