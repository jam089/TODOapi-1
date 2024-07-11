from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr

from core.utils import camel_to_snake


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_to_snake(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True)
