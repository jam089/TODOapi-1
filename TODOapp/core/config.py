from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pydantic import BaseModel, PostgresDsn


class RunCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class APICfg(BaseModel):
    prefix: str = "/api"


class DBCfg(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class Settings(BaseSettings):
    run: RunCfg = RunCfg()
    api: APICfg = APICfg()
    db: DBCfg


settings = Settings()
