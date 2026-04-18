"""環境変数から共有設定を読み込むユーティリティ。"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Web API アプリ全体で共有する設定。"""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
        validate_default=True,
    )

    app_name: str = Field(
        default="fastapi-architecture-lab API",
        min_length=1,
        validation_alias="APP_NAME",
    )
    app_env: str = Field(
        default="development",
        min_length=1,
        validation_alias="APP_ENV",
    )
    debug: bool = Field(
        default=False,
        validation_alias="APP_DEBUG",
    )
    favorites_csv_path: Path = Field(
        default=Path("data/favorites.csv"),
        validation_alias="FAVORITES_CSV_PATH",
    )
