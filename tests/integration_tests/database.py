from typing import AsyncGenerator

import pytest
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from core.models import db_helper, Base

from core.config import settings
from main import todo_app


test_engine = create_async_engine(
    url=str(settings.db.url),
    poolclass=NullPool,
)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def override_dispose() -> None:
    await test_engine.dispose()


async def override_session_getter() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


todo_app.dependency_overrides[db_helper.session_getter] = override_session_getter
todo_app.dependency_overrides[db_helper.dispose] = override_dispose


def pytest_addoption(parser):
    parser.addoption(
        "--skip-delete-endpoints",
        action="store_true",
        default=False,
        help="skipping delete endpoints to save data in DB",
    )
    parser.addoption(
        "--skip-delete-DB",
        action="store_true",
        default=False,
        help="skipping delete DB part to save data in DB",
    )


def pytest_configure(config):
    if config.getoption("--skip-delete-endpoints"):
        return
    if config.getoption("--skip-delete-DB"):
        return


@pytest.fixture(autouse=True)
async def prepare_db(request):
    assert settings.db.mode == "TEST"
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_session_factory() as conn:
        await conn.begin()
        await conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION update_last_update_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.last_update_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
            )
        )
        await conn.commit()
        await conn.execute(
            text(
                """
            CREATE TRIGGER last_update_trigger
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_last_update_column();
            """
            )
        )
        await conn.commit()
    yield
    if not (
        request.config.getoption("--skip-delete-DB")
        or request.config.getoption("--skip-delete-endpoints")
    ):
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(todo_app),
        base_url=f"http://test{settings.api.prefix}",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac


@pytest.fixture
async def auth_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(todo_app),
        base_url=f"http://test_{settings.api.prefix}",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac
