from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseTask(BaseModel):
    pass


class CreateTaskSchm(BaseTask):
    name: str
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    scheduled_hours: int


class UpdateTaskSchm(BaseTask):
    name: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    scheduled_hours: int | None = None
    status: str | None = None


class ChangeTaskUserSchm(BaseTask):
    user_id: int


class SearchTaskSchm(BaseTask):
    id: int | None = None
    name: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    user_id: int | None = None
    status: str | None = None


class TaskSchm(CreateTaskSchm):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    last_update_at: datetime | None = None
    user_id: int
