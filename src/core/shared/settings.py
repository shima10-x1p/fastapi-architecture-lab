"""環境変数と .env ファイルから読み込むアプリケーション設定。

環境変数ではすべての項目に APP_ プレフィックスを付ける
（例: APP_LOG_LEVEL）。
シングルトンの設定は get_settings() から取得する。
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# APP_LOG_FORMAT が未設定の場合に使う Python のログフォーマット文字列。
# 可読性のため、タイムスタンプ・レベル・ロガー名・メッセージを含める。
_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


class Settings(BaseSettings):
    """アプリケーション設定を一元管理する。

    値は次の優先順位で読み込まれる:
    1. 環境変数
    2. 作業ディレクトリの .env ファイル
    3. このクラスで定義したデフォルト値
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        # 未知の環境変数は無視し、adapter 側の設定拡張を容易にする
        extra="ignore",
    )

    app_name: str = Field(default="fastapi-architecture-lab")
    env: Literal["dev", "staging", "prod"] = Field(default="dev")
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default=_DEFAULT_LOG_FORMAT,
        description=(
            "ルートロガーに適用する Python のログフォーマット文字列。"
            "logging.LogRecord が提供する任意の属性を利用できる"
            "（例: %(asctime)s, %(levelname)s, %(name)s, %(message)s）。"
        ),
    )
    debug: bool = Field(default=False)
    open_library_base_url: str = Field(default="https://openlibrary.org")
    open_library_timeout_seconds: float = Field(default=5.0, gt=0)
    open_library_user_agent: str = Field(
        default="fastapi-architecture-lab/0.1.0"
    )
    open_library_contact_email: str
    open_library_cache_ttl_seconds: int = Field(default=300, ge=1)

    @field_validator("open_library_base_url")
    @classmethod
    def normalize_open_library_base_url(cls, value: str) -> str:
        """Open Library の base URL 末尾スラッシュを正規化する。"""
        normalized_value = value.strip().rstrip("/")
        if not normalized_value:
            raise ValueError("Open Library の base URL は必須です。")
        return normalized_value

    @field_validator("open_library_user_agent")
    @classmethod
    def validate_open_library_user_agent(cls, value: str) -> str:
        """Open Library へ送る User-Agent が空でないことを保証する。"""
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Open Library の User-Agent は必須です。")
        return normalized_value

    @field_validator("open_library_contact_email")
    @classmethod
    def validate_open_library_contact_email(cls, value: str) -> str:
        """Open Library へ連絡先として渡すメールアドレスを検証する。"""
        normalized_value = value.strip()
        if not normalized_value or "@" not in normalized_value:
            raise ValueError(
                "Open Library の contact email には有効なメールアドレスが必要です。"
            )
        return normalized_value

    @property
    def open_library_identifying_user_agent(self) -> str:
        """Open Library 向けの識別付き User-Agent を返す。"""
        return (
            f"{self.open_library_user_agent}"
            f" (contact: {self.open_library_contact_email})"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """シングルトンの Settings インスタンスを返す。

    1 回目の呼び出し結果はキャッシュされる。テストでは環境変数を
    差し替える前に get_settings.cache_clear() を呼び出し、
    新しいインスタンスが生成されるようにする。
    """
    return Settings()
