import factory

from core.models import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    username = factory.Faker("user_name")
    name = factory.Faker("name")
    b_date = factory.Faker("date_of_birth")
