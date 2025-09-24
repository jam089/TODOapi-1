from datetime import timedelta
from typing import Type

import factory

from core.config import settings
from core.models import User, Task
from tests.integration_tests.database import test_session_factory


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    username = factory.Faker("user_name")
    name = factory.Faker("name")
    b_date = factory.Faker("date_of_birth")


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Task
        sqlalchemy_session_persistence = "flush"

    name = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph", nb_sentences=3)
    start_at = factory.Faker("date_time_this_year")
    end_at = factory.LazyAttribute(lambda o: o.start_at + timedelta(hours=2))
    scheduled_hours = factory.Faker("random_int", min=1, max=16)
    status = factory.Iterator(settings.tstat.model_dump().values())
    user = factory.SubFactory(UserFactory)


async def create(factory_class: Type[factory.alchemy.SQLAlchemyModelFactory], **kwargs):
    obj = factory_class.build(**kwargs)
    async with test_session_factory() as session:
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj
