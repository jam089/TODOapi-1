import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from api.schemas.task import TaskSchm
from core.crud import task as task_crud


@pytest.mark.asyncio
async def test_endpoint_get_all_tasks(
    async_client: AsyncClient,
    test_session: AsyncSession,
    admin_user: dict,
    test_task_a: dict,
    test_user_b: dict,
):
    response = await async_client.get(
        url=f"{settings.api.task.prefix}/all/",
        headers=admin_user.get("headers"),
    )
    assert response.status_code == 200
    tasks = await task_crud.get_all_tasks(test_session)
    expected = [TaskSchm.model_validate(t).model_dump(mode="json") for t in tasks]
    assert response.json() == expected
