"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    google_api_key: str = Field(..., description="Google Gemini API key")
    llm_model: str = Field(
        default="gemini-3.8-flash",
        description="Gemini model to use for analysis",
    )
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=4000, description="Server port")
    request_timeout: int = Field(
        default=30, description="Timeout for website fetching (seconds)"
    )
    llm_timeout: int = Field(
        default=120, description="Timeout for LLM requests (seconds)"
    )
    max_content_length: int = Field(
        default=50000,
        description="Maximum characters of website content to send to LLM",
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


def get_settings_override(**overrides) -> Settings:
    """Create settings with overrides — useful for testing."""
    defaults = {
        "google_api_key": "test-key",
        "llm_model": "gemini-2.5-flash",
    }
    defaults.update(overrides)
    return Settings(**defaults)

