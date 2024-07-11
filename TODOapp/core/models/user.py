from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from core.models import Base

if TYPE_CHECKING:
    from core.models import Task


class User(Base):
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True, server_default="1")

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
