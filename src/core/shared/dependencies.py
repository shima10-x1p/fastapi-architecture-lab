"""FastAPI で共有設定を注入するための依存関係定義。"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from core.shared.settings import AppSettings


@lru_cache
def get_settings() -> AppSettings:
    """環境変数から共有設定を読み込み、キャッシュして返す。"""

    return AppSettings()


def clear_settings_cache() -> None:
    """テストや再読み込み向けに設定キャッシュを破棄する。"""

    get_settings.cache_clear()


type SettingsDependency = Annotated[AppSettings, Depends(get_settings)]
