from pydantic import BaseModel


class TokenInfoSchm(BaseModel):
    access_token: str
    refresh_token: str | None = None
