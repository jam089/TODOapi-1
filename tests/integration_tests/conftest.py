from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from core.config import settings
from main import todo_app


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(todo_app),
        base_url=f"http://test{settings.api.prefix}",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac
