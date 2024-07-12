from datetime import date

from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    username: str
    name: str | None = None
    b_date: date | None = None
    active: bool | None = None


class CreateUser(BaseUser):
    password: str | bytes


class UpdateUser(BaseUser):
    username: str | None = None
    name: str | None = None
    b_date: date | None = None
    active: bool | None = None


class User(BaseUser):
    model_config = ConfigDict(from_attributes=True)

    id: int
