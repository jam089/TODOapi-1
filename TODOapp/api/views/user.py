from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from api.schemas import UserSchm
from core.crud import user

router = APIRouter()


@router.get("/", response_model=Sequence[UserSchm])
async def get_all_users(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await user.get_all_users(session)
