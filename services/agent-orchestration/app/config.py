from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).parents[3] / ".env"

class Settings(BaseSettings):
    llm_gateway_url: str = "http://localhost:4000"
    litellm_master_key: str = "dev-litellm-key"
    simulation_engine_url: str = "http://localhost:8001"
    log_level: str = "INFO"

    # Model routing - names must match what litellm_config.yaml registers
    fast_model: str = "groq/llama-3.1-8b-instant"  # profile + params
    narrator_model: str = "groq/llama-3.3-70b-versatile"  # longer prose
    guardrail_model: str = "anthropic/claude-haiku-4-5"  # safety-critical

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()