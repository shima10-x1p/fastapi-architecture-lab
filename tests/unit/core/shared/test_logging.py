"""core.shared.logging のユニットテスト。"""

import logging

import pytest

from core.shared.logging import configure_logging, get_logger
from core.shared.settings import Settings


@pytest.fixture(autouse=True)
def reset_root_logger():
    """テスト間汚染を避けるため、各テスト後に root logger を復元する。"""
    root = logging.getLogger()
    original_level = root.level
    original_handlers = root.handlers[:]
    yield
    root.setLevel(original_level)
    root.handlers = original_handlers


def _make_settings(**kwargs) -> Settings:
    """テスト向けのデフォルト値で Settings インスタンスを組み立てる。"""
    defaults = {
        "app_name": "test-app",
        "env": "dev",
        "log_level": "INFO",
        "log_format": "%(levelname)s %(name)s %(message)s",
        "debug": False,
    }
    defaults.update(kwargs)
    return Settings.model_validate(defaults)


class TestGetLogger:
    """get_logger が適切な名前の Logger を返すこと。"""

    def test_returns_logger_instance(self):
        logger = get_logger("mymodule")
        assert isinstance(logger, logging.Logger)

    def test_logger_name_matches_argument(self):
        logger = get_logger("core.domain.book")
        assert logger.name == "core.domain.book"

    def test_dunder_name_pattern(self):
        # 一般的な呼び出し方 get_logger(__name__) を再現する
        logger = get_logger(__name__)
        assert logger.name == __name__


class TestConfigureLogging:
    """configure_logging が Settings から root logger を構成すること。"""

    def test_sets_root_level_info(self):
        configure_logging(_make_settings(log_level="INFO"))
        assert logging.getLogger().level == logging.INFO

    def test_sets_root_level_debug(self):
        configure_logging(_make_settings(log_level="DEBUG"))
        assert logging.getLogger().level == logging.DEBUG

    def test_sets_root_level_warning(self):
        configure_logging(_make_settings(log_level="WARNING"))
        assert logging.getLogger().level == logging.WARNING

    def test_unknown_level_falls_back_to_info(self):
        # 不正なレベル文字列でもログが完全に無音にならないこと
        configure_logging(_make_settings(log_level="NONSENSE"))
        assert logging.getLogger().level == logging.INFO

    def test_adds_stream_handler(self):
        configure_logging(_make_settings())
        handlers = logging.getLogger().handlers
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)

    def test_applies_custom_log_format(self):
        custom_fmt = "%(levelname)s | %(message)s"
        configure_logging(_make_settings(log_format=custom_fmt))
        handler = logging.getLogger().handlers[0]
        assert handler.formatter._fmt == custom_fmt

    def test_repeated_calls_do_not_duplicate_handlers(self):
        configure_logging(_make_settings())
        configure_logging(_make_settings())
        root_handlers = logging.getLogger().handlers
        stream_handlers = [h for h in root_handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) == 1
