from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func

from core.models import Base


class User(Base):
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True, server_default="1")
