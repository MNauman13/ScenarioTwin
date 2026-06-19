from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).parents[3] / ".env"

class Settings(BaseSettings):
    database_url: str
    log_level: str = "INFO"
    n_simulation_paths: int = 10_000
    simulation_years: int = 30
    random_seed: int = 42

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()