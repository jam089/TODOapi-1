from typing import Type

import factory

from core.models import User
from tests.integration_tests.database import test_session_factory


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    username = factory.Faker("user_name")
    name = factory.Faker("name")
    b_date = factory.Faker("date_of_birth")


async def create(factory_class: factory.alchemy.SQLAlchemyModelFactory, **kwargs):
async def create(factory_class: Type[factory.alchemy.SQLAlchemyModelFactory], **kwargs):
    obj = factory_class.build(**kwargs)
    async with test_session_factory() as session:
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj
