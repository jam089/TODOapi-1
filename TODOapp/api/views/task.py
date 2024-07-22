from typing import Annotated, Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.validation import get_currant_auth_user_with_admin
from api.schemas import TaskSchmExtended, UserSchmExtended
from core.models import db_helper
from core.crud import task as crud

router = APIRouter()


@router.get("/all-tasks/", response_model=Sequence[TaskSchmExtended])
async def get_all_tasks(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    admin: Annotated[UserSchmExtended, Depends(get_currant_auth_user_with_admin)],
):
    return await crud.get_all_tasks(session)
