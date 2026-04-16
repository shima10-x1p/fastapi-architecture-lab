"""Web API 全体で利用する共通 logger ユーティリティ。"""

import logging
import os
import sys

APP_LOG_LEVEL_ENV_VAR = "APP_LOG_LEVEL"
APP_LOG_FORMAT_ENV_VAR = "APP_LOG_FORMAT"

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

_STDOUT_HANDLER_NAME = "core.shared.stdout"


def configure_logging(
    *,
    level_name: str | None = None,
    log_format: str | None = None,
) -> logging.Logger:
    """
    アプリ共通の logging 設定を初期化する。

    Args:
        level_name (str | None): ログレベルの明示指定値。
        log_format (str | None): ログフォーマットの明示指定値。

    Returns:
        logging.Logger: 初期化済みのルートロガー。

    Exceptions:
        ValueError: ログレベルまたはログフォーマットが不正な場合に発生。
    """
    resolved_level_name = _read_log_level_name(level_name)
    resolved_level = _resolve_log_level(resolved_level_name)
    resolved_log_format = _resolve_log_format(_read_log_format(log_format))
    root_logger = logging.getLogger()
    stdout_handler = _get_or_create_stdout_handler(root_logger)

    stdout_handler.setLevel(resolved_level)
    stdout_handler.setFormatter(logging.Formatter(resolved_log_format))
    root_logger.setLevel(resolved_level)

    return root_logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    利用箇所ごとの logger を返す。

    Args:
        name (str | None): ロガー名。未指定時はルートロガーを返す。

    Returns:
        logging.Logger: 指定名に対応するロガー。
    """
    return logging.getLogger(name)


def _read_log_level_name(level_name: str | None) -> str:
    """
    ログレベル設定値を取得する。

    Args:
        level_name (str | None): 呼び出し元からの明示指定値。

    Returns:
        str: 解決済みのログレベル名。
    """
    if level_name is not None:
        return level_name

    return os.getenv(APP_LOG_LEVEL_ENV_VAR, DEFAULT_LOG_LEVEL)


def _read_log_format(log_format: str | None) -> str:
    """
    ログフォーマット設定値を取得する。

    Args:
        log_format (str | None): 呼び出し元からの明示指定値。

    Returns:
        str: 解決済みのログフォーマット。
    """
    if log_format is not None:
        return log_format

    return os.getenv(APP_LOG_FORMAT_ENV_VAR, DEFAULT_LOG_FORMAT)


def _resolve_log_level(level_name: str) -> int:
    """
    ログレベル名を logging 用の数値へ変換する。

    Args:
        level_name (str): 文字列のログレベル。

    Returns:
        int: logging が扱う数値のログレベル。

    Exceptions:
        ValueError: 文字列が空、または未対応のログレベルの場合に発生。
    """
    normalized_level_name = level_name.strip()
    if not normalized_level_name:
        raise ValueError(f"{APP_LOG_LEVEL_ENV_VAR} には空文字列を設定できません。")

    if normalized_level_name.isdigit():
        return int(normalized_level_name)

    resolved_level = logging.getLevelName(normalized_level_name.upper())
    if not isinstance(resolved_level, int):
        raise ValueError(
            f"{APP_LOG_LEVEL_ENV_VAR} に未対応の値が設定されています: {level_name!r}"
        )

    return resolved_level


def _resolve_log_format(log_format: str) -> str:
    """
    ログフォーマット文字列を検証する。

    Args:
        log_format (str): 文字列のログフォーマット。

    Returns:
        str: 利用可能なログフォーマット。

    Exceptions:
        ValueError: フォーマットが空文字列の場合に発生。
    """
    if not log_format.strip():
        raise ValueError(f"{APP_LOG_FORMAT_ENV_VAR} には空文字列を設定できません。")

    return log_format


def _get_or_create_stdout_handler(
    logger: logging.Logger,
) -> logging.StreamHandler:
    """
    標準出力向けハンドラーを取得し、未作成なら追加する。

    Args:
        logger (logging.Logger): 設定対象のロガー。

    Returns:
        logging.StreamHandler: 共通で再利用する標準出力ハンドラー。
    """
    existing_handler = _find_stdout_handler(logger)
    if existing_handler is not None:
        return existing_handler

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.set_name(_STDOUT_HANDLER_NAME)
    logger.addHandler(stdout_handler)

    return stdout_handler


def _find_stdout_handler(
    logger: logging.Logger,
) -> logging.StreamHandler | None:
    """
    既存の共通標準出力ハンドラーを探索する。

    Args:
        logger (logging.Logger): 探索対象のロガー。

    Returns:
        logging.StreamHandler | None: 見つかったハンドラー。未登録なら None。
    """
    for handler in logger.handlers:
        if (
            isinstance(handler, logging.StreamHandler)
            and handler.get_name() == _STDOUT_HANDLER_NAME
        ):
            return handler

    return None
