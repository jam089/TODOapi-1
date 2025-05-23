from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from core.models import Base
from core.config import settings

if TYPE_CHECKING:
    from core.models import Task


class User(Base):
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True, server_default="1")
    name: Mapped[str | None] = mapped_column(String(32))
    b_date: Mapped[date | None]
    role: Mapped[str] = mapped_column(
        default=settings.roles.user,
        server_default=str(settings.roles.user),
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
