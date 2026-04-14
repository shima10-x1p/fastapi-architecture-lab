"""環境変数と .env ファイルから読み込むアプリケーション設定。

環境変数ではすべての項目に APP_ プレフィックスを付ける
（例: APP_LOG_LEVEL）。
シングルトンの設定は get_settings() から取得する。
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """シングルトンの Settings インスタンスを返す。

    1 回目の呼び出し結果はキャッシュされる。テストでは環境変数を
    差し替える前に get_settings.cache_clear() を呼び出し、
    新しいインスタンスが生成されるようにする。
    """
    return Settings()
