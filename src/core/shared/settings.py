"""Application settings loaded from environment variables and .env file.

All fields are prefixed with APP_ in the environment (e.g. APP_LOG_LEVEL).
Call get_settings() to obtain the singleton instance.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Python logging format string used when APP_LOG_FORMAT is not set.
# Includes timestamp, level, logger name, and message for quick readability.
_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


class Settings(BaseSettings):
    """Centralised application configuration.

    Values are read (in priority order) from:
    1. Environment variables
    2. .env file in the working directory
    3. Field defaults defined here
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        # Ignore unknown env vars so adapter-level settings can extend freely
        extra="ignore",
    )

    app_name: str = Field(default="fastapi-architecture-lab")
    env: Literal["dev", "staging", "prod"] = Field(default="dev")
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default=_DEFAULT_LOG_FORMAT,
        description=(
            "Python logging format string applied to the root logger. "
            "Any attribute supported by logging.LogRecord is available "
            "(e.g. %(asctime)s, %(levelname)s, %(name)s, %(message)s)."
        ),
    )
    debug: bool = Field(default=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton Settings instance.

    The result is cached after the first call. In tests, call
    get_settings.cache_clear() before patching environment variables to ensure
    a fresh instance is created.
    """
    return Settings()
