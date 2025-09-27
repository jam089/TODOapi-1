from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class RunCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class DBCfg(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    mode: str


class TaskStatuses(BaseModel):
    pld: str = "Planned"  # Planned
    atw: str = "At work"  # At work
    cmp: str = "Completed"  # Completed
    dly: str = "Delayed"  # Delayed


class UserRole(BaseModel):
    user: str = "User"
    admin: str = "Admin"


class AuthCookies(BaseModel):
    http_only: bool = True
    secure: bool = False
    samesite: Literal["lax", "strict", "none"] = "lax"
    path: str = "/"


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 40
    prefix: str = "/auth"
    tag: str = "Auth"
    cookies: AuthCookies = AuthCookies()


class UserAPI(BaseModel):
    prefix: str = "/user"
    tag: str = "User"


class TaskAPI(BaseModel):
    prefix: str = "/task"
    tag: str = "Task"


class APICfg(BaseModel):
    prefix: str = "/api"
    user: UserAPI = UserAPI()
    task: TaskAPI = TaskAPI()
    auth_jwt: AuthJWT = AuthJWT()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env.template", ".env"],
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="TODOAPP__",
    )

    run: RunCfg = RunCfg()
    api: APICfg = APICfg()
    tstat: TaskStatuses = TaskStatuses()
    roles: UserRole = UserRole()
    db: DBCfg


settings = Settings()
