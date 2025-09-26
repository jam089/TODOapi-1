from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from core.config import settings
from core.models import db_helper
from api import router as api_router
from core.utils.on_startup_scripts import check_and_create_superuser


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.session_factory() as session:
        await check_and_create_superuser(session)
    yield
    await db_helper.dispose()


todo_app = FastAPI(lifespan=lifespan)

todo_app.include_router(api_router)


def main():
    uvicorn.run(
        "main:todo_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )


if __name__ == "__main__":
    main()
