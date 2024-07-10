from pydantic_settings import BaseSettings
from pydantic import BaseModel


class RunCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class APICfg(BaseModel):
    prefix: str = "/api"


class Settings(BaseSettings):
    run: RunCfg = RunCfg()
    api: APICfg = APICfg()


settings = Settings()
