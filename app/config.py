from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = Field(default="dev", description="dev | prod")
    log_level: str = "INFO"

    anthropic_api_key: str = Field(..., description="From console.anthropic.com")
    anthropic_model: str = "claude-haiku-4-5"
    anthropic_max_tokens: int = 1024
    anthropic_timeout_s: float = 30.0


settings = Settings()
