import re
from string import Template

from core.config import settings
from core.models import User
from httpx import AsyncClient


async def authentication(async_client: AsyncClient, user: User, password: str):
    request_json = {
        "username": user.username,
        "password": password,
    }
    response = await async_client.post(
        url=f"{settings.api.auth_jwt.prefix}/login/",
        data=request_json,
    )
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "headers": {"Authorization": f"Bearer {access_token}"},
    }


def template_matches(
    template: Template,
    msg: str,
    placeholder: str,
    pattern: str = r".+",
) -> bool:
    regex = re.escape(template.template)
    regex = regex.replace(rf"\${placeholder}", pattern)
    return re.fullmatch(regex, msg) is not None
