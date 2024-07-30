import pytest

from core.models import db_helper, Base


@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    assert settings.db.mode == "TEST"
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
