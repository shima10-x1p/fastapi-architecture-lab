"""アプリケーションのエントリーポイント。"""

from __future__ import annotations

from fastapi import FastAPI

from core.adapters.inbound.favorites_router import router as favorites_router
from core.shared.dependencies import get_settings

_APP_DESCRIPTION = (
    "Python 3.14 + FastAPI による Ports and Adapters アーキテクチャの検証 Lab。"
    " お気に入り YouTube 動画の管理と、埋め込みプレイヤー HTML の取得を提供する。"
)
_APP_VERSION = "0.1.0"

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=_APP_DESCRIPTION,
    version=_APP_VERSION,
    debug=settings.debug,
)
app.include_router(favorites_router)
