from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    username: str
    name: str | None = None
    b_date: date | None = None


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
    active: bool


class UserSchmExtended(UserSchm):
    created_at: datetime
    last_update_at: datetime | None
    role: str


class UserPassChangeSchm(BaseModel):
    password: str | bytes


class UserRoleChangeSchm(BaseModel):
    role: str
