from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).parents[3] / ".env"


class Settings(BaseSettings):
    database_url:            str
    redis_url:               str = "redis://localhost:6379/0"
    api_secret_key:          str
    jwt_algorithm:           str = "HS256"
    jwt_expire_minutes:      int = 60
    simulation_engine_url:   str = "http://localhost:8001"
    agent_orchestration_url: str = "http://localhost:8002"
    log_level:               str = "INFO"
    environment:             str = "development"

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
