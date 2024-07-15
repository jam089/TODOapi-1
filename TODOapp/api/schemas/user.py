from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    username: str
    name: str | None = None
    b_date: date | None = None
    active: bool | None = None


class CreateUserSchm(BaseUser):
    password: str | bytes


class UpdateUserSchm(BaseUser):
    username: str | None = None
    name: str | None = None
    b_date: date | None = None
    active: bool | None = None


class UserSchm(BaseUser):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserSchmExtended(UserSchm):
    created_at: datetime
    last_update_at: datetime | None
