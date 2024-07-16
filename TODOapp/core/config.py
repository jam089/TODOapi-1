from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn

BASE_DIR = Path(__file__).parent.parent


class RunCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


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


class DBCfg(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class TaskStatuses(BaseModel):
    pld: str = "Planned"  # Planned
    atw: str = "At work"  # At work
    cmp: str = "Completed"  # Completed
    dly: str = "Delayed"  # Delayed


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
    db: DBCfg


settings = Settings()
