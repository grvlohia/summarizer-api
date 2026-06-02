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
    anthropic_max_retries: int = 3

    # Postgres
    database_url: str = Field(..., description="Database URL")
    # redis url
    redis_url: str = Field(..., description="Redis URL")

    # Auth
    master_api_key: str = Field(..., description="For /v1/keys admin endpoints. 32+ chars.")
    api_key_prefix: str = "sk_live_"

    # Rate limiting
    rate_limit_capacity: int = 60  # tokens (= requests) in the bucket
    rate_limit_refill_per_minute: int = 60  # tokens added per 60s


settings = Settings()
