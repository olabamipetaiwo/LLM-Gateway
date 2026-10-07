from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    default_provider: str = "ollama"

    # local
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma4"

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"

    # Anthropic
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    max_output_tokens: int = Field(default=1024, gt=0)
    llm_timeout_seconds: float = Field(default=30.0, gt=0.0, description="Timeout for LLM API calls in seconds.")

    llm_max_attempts: int = 3
    llm_retry_initial_delay: float = 0.5
    llm_retry_max_delay: float = 8.0


# @lru_cache makes later calls return the same object, avoiding repeated loading.
# access it as settings = get_settings
@lru_cache
def get_settings() -> Settings:
    return Settings()
