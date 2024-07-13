from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from core.config import settings
from core.models import db_helper
from api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield
    await db_helper.dispose()


todo_app = FastAPI(lifespan=lifespan)

todo_app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:todo_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
