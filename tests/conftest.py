import pytest

from core.models import db_helper, Base

from core.config import settings


@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    assert settings.db.mode == "TEST"
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def jwt_config():
    jwt_config = {
        "private_key": settings.api.auth_jwt.private_key_path.read_text(),
        "public_key": settings.api.auth_jwt.public_key_path.read_text(),
        "algorithm": settings.api.auth_jwt.algorithm,
        "expire_minutes": 15,
    }
    return jwt_config
