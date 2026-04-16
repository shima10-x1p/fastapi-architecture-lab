"""共通 logger ユーティリティの unit test。"""

import logging
import sys
from collections.abc import Iterator

import pytest

from core.shared.logger import (
    APP_LOG_FORMAT_ENV_VAR,
    APP_LOG_LEVEL_ENV_VAR,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    configure_logging,
    get_logger,
)

_STDOUT_HANDLER_NAME = "core.shared.stdout"


@pytest.fixture
def isolate_root_logger() -> Iterator[None]:
    """
    各テストでルートロガーの状態を隔離する。

    Yields:
        Iterator[None]: テスト本体の実行制御。
    """
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    yield

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        if handler not in original_handlers:
            handler.close()

    root_logger.setLevel(original_level)
    for handler in original_handlers:
        root_logger.addHandler(handler)


def _find_configured_stdout_handler(
    root_logger: logging.Logger,
) -> logging.StreamHandler:
    """
    テスト対象の標準出力ハンドラーを取得する。

    Args:
        root_logger (logging.Logger): 探索対象のルートロガー。

    Returns:
        logging.StreamHandler: 共通 logger ユーティリティが追加したハンドラー。

    Exceptions:
        AssertionError: 期待するハンドラーが存在しない場合に発生。
    """
    for handler in root_logger.handlers:
        if (
            isinstance(handler, logging.StreamHandler)
            and handler.get_name() == _STDOUT_HANDLER_NAME
        ):
            return handler

    raise AssertionError("共通標準出力ハンドラーが見つかりません。")


def test_configure_logging_uses_default_settings_when_env_vars_are_missing(
    isolate_root_logger: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    環境変数が未設定ならデフォルト値で初期化されることを確認する。

    Args:
        isolate_root_logger (None): ルートロガーを隔離する fixture。
        monkeypatch (pytest.MonkeyPatch): 環境変数操作用 fixture。
    """
    monkeypatch.delenv(APP_LOG_LEVEL_ENV_VAR, raising=False)
    monkeypatch.delenv(APP_LOG_FORMAT_ENV_VAR, raising=False)

    root_logger = configure_logging()
    handler = _find_configured_stdout_handler(root_logger)

    assert root_logger.level == logging.getLevelName(DEFAULT_LOG_LEVEL)
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stdout
    assert handler.formatter is not None
    assert handler.formatter._fmt == DEFAULT_LOG_FORMAT


def test_configure_logging_applies_env_var_settings(
    isolate_root_logger: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    環境変数のログレベルとフォーマットが反映されることを確認する。

    Args:
        isolate_root_logger (None): ルートロガーを隔離する fixture。
        monkeypatch (pytest.MonkeyPatch): 環境変数操作用 fixture。
    """
    custom_format = "%(levelname)s|%(name)s|%(message)s"
    monkeypatch.setenv(APP_LOG_LEVEL_ENV_VAR, "DEBUG")
    monkeypatch.setenv(APP_LOG_FORMAT_ENV_VAR, custom_format)

    root_logger = configure_logging()
    handler = _find_configured_stdout_handler(root_logger)

    assert root_logger.level == logging.DEBUG
    assert handler.level == logging.DEBUG
    assert handler.formatter is not None
    assert handler.formatter._fmt == custom_format


def test_configure_logging_does_not_duplicate_stdout_handler(
    isolate_root_logger: None,
) -> None:
    """
    初期化を複数回呼んでも標準出力ハンドラーが重複しないことを確認する。

    Args:
        isolate_root_logger (None): ルートロガーを隔離する fixture。
    """
    root_logger = configure_logging()
    first_handler = _find_configured_stdout_handler(root_logger)

    configure_logging()

    configured_handlers = [
        handler
        for handler in root_logger.handlers
        if isinstance(handler, logging.StreamHandler)
        and handler.get_name() == _STDOUT_HANDLER_NAME
    ]

    assert len(configured_handlers) == 1
    assert configured_handlers[0] is first_handler


def test_configure_logging_rejects_invalid_log_level(
    isolate_root_logger: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    不正なログレベル文字列を拒否することを確認する。

    Args:
        isolate_root_logger (None): ルートロガーを隔離する fixture。
        monkeypatch (pytest.MonkeyPatch): 環境変数操作用 fixture。
    """
    monkeypatch.setenv(APP_LOG_LEVEL_ENV_VAR, "INVALID")

    with pytest.raises(ValueError, match=APP_LOG_LEVEL_ENV_VAR):
        configure_logging()


def test_get_logger_returns_named_logger() -> None:
    """
    指定名に対応する logger を取得できることを確認する。
    """
    logger = get_logger("core.shared.test")

    assert logger.name == "core.shared.test"
