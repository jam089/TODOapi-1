from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from core.models import Base
from core.config import settings

if TYPE_CHECKING:
    from core.models import User


class Task(Base):
    name: Mapped[str] = mapped_column(String(70))
    description: Mapped[str | None] = mapped_column(String(360))
    start_at: Mapped[datetime | None]
    end_at: Mapped[datetime | None]
    scheduled_hours: Mapped[int] = mapped_column(default=0, server_default="0")
    status: Mapped[str] = mapped_column(
        default=settings.tstat.pld,
        server_default=settings.tstat.pld,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="tasks")
