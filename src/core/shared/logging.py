"""ロギング設定用のヘルパー。

利用パターン
------------
アプリケーション起動時（例: FastAPI の lifespan）:

    from core.shared.logging import configure_logging
    from core.shared.settings import get_settings

    configure_logging(get_settings())

任意のモジュール内では:

    from core.shared.logging import get_logger

    logger = get_logger(__name__)
    logger.info("処理を実行しました")
"""

import logging

from core.shared.settings import Settings


def configure_logging(settings: Settings) -> None:
    """Settings の値を使ってルートロガーを設定する。

    アプリケーション起動時に 1 回だけ呼ぶことを想定するが、
    テスト用途では後続呼び出しでその場で再設定できる。

    ログレベルは logging.getLevelName で解決するため、
    文字列名（"INFO"）と数値の両方を扱える。
    不正なレベル文字列は INFO にフォールバックし、
    ログ出力が無音になることを防ぐ。
    """
    level = logging.getLevelName(settings.log_level.upper())
    if not isinstance(level, int):
        # 未知の名前では getLevelName が "Level 99" のような文字列を返す
        level = logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # テストでの再呼び出しを冪等にするため、既存ハンドラをすべて置換する
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(settings.log_format))
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """名前付きロガーを返す。

    呼び出し元モジュールの __name__ を渡すと、そのモジュールに
    スコープされたロガーを取得できる。返されるロガーの実効レベルは
    configure_logging() で設定したルートロガーを継承する。
    """
    return logging.getLogger(name)
