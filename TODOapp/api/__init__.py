from fastapi import APIRouter

from core.config import settings

from .views.user import router as user_router
from .views.task import router as task_router
from .auth.auth import router as auth_router

router = APIRouter(prefix=settings.api.prefix)
router.include_router(
    router=user_router,
    prefix=settings.api.user.prefix,
    tags=[settings.api.user.tag],
)
router.include_router(
    router=task_router,
    prefix=settings.api.task.prefix,
    tags=[settings.api.task.tag],
)
router.include_router(
    router=auth_router,
    prefix=settings.api.auth_jwt.prefix,
    tags=[settings.api.auth_jwt.tag],
)
