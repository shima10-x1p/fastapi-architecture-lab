"""core.shared.logging のユニットテスト。"""

import logging
from collections.abc import Iterator

import pytest

from core.shared.logging import configure_logging, get_logger
from core.shared.settings import Settings


@pytest.fixture(autouse=True)
def restore_root_logger() -> Iterator[None]:
    """各テスト後に root logger のレベルとハンドラを復元する。"""
    root = logging.getLogger()
    original_level = root.level
    original_handlers = root.handlers[:]

    yield

    for handler in root.handlers[:]:
        root.removeHandler(handler)
        if handler not in original_handlers:
            handler.close()

    root.setLevel(original_level)

    for handler in original_handlers:
        root.addHandler(handler)


def _make_settings(**overrides: object) -> Settings:
    """logging テストで使う Settings を最小構成で組み立てる。"""
    defaults: dict[str, object] = {
        "app_name": "test-app",
        "env": "dev",
        "log_level": "INFO",
        "log_format": "%(levelname)s %(name)s %(message)s",
        "debug": False,
    }
    defaults.update(overrides)
    return Settings.model_validate(defaults)


class TestGetLogger:
    """get_logger() が名前付き Logger を返すことを検証する。"""

    def test_returns_logger_with_requested_name(self) -> None:
        # 準備
        logger_name = "core.shared.logging"

        # 実行
        logger = get_logger(logger_name)

        # 検証
        assert isinstance(logger, logging.Logger)
        assert logger is logging.getLogger(logger_name)
        assert logger.name == logger_name


class TestConfigureLogging:
    """configure_logging() の root logger 再設定を検証する。"""

    @pytest.mark.parametrize(
        ("configured_level", "expected_level"),
        [
            ("INFO", logging.INFO),
            ("debug", logging.DEBUG),
            ("WARNING", logging.WARNING),
        ],
    )
    def test_configures_root_and_handler_levels_from_setting(
        self, configured_level: str, expected_level: int
    ) -> None:
        # 準備
        settings = _make_settings(log_level=configured_level)

        # 実行
        configure_logging(settings)
        root = logging.getLogger()
        handler = root.handlers[0]

        # 検証
        assert root.level == expected_level
        assert handler.level == expected_level

    def test_replaces_existing_handlers_with_single_stream_handler(self) -> None:
        # 準備
        root = logging.getLogger()
        old_stream_handler = logging.StreamHandler()
        old_null_handler = logging.NullHandler()
        root.addHandler(old_stream_handler)
        root.addHandler(old_null_handler)

        # 実行
        configure_logging(_make_settings())

        # 検証
        assert len(root.handlers) == 1
        assert type(root.handlers[0]) is logging.StreamHandler
        assert root.handlers[0] is not old_stream_handler
        assert old_null_handler not in root.handlers

    def test_applies_requested_formatter_to_installed_handler(self) -> None:
        # 準備
        custom_format = "%(levelname)s | %(message)s"

        # 実行
        configure_logging(_make_settings(log_format=custom_format))
        handler = logging.getLogger().handlers[0]

        # 検証
        assert handler.formatter is not None
        assert handler.formatter._fmt == custom_format

    def test_falls_back_to_info_for_unknown_log_level(self) -> None:
        # 準備
        settings = _make_settings(log_level="not-a-level")

        # 実行
        configure_logging(settings)

        # 検証
        assert logging.getLogger().level == logging.INFO

    def test_reconfiguration_keeps_single_handler_and_updates_formatter(self) -> None:
        # 準備
        configure_logging(_make_settings(log_format="%(message)s"))
        first_handler = logging.getLogger().handlers[0]
        updated_format = "%(levelname)s %(message)s"

        # 実行
        configure_logging(
            _make_settings(log_level="WARNING", log_format=updated_format)
        )
        root = logging.getLogger()

        # 検証
        assert root.level == logging.WARNING
        assert len(root.handlers) == 1
        assert root.handlers[0] is not first_handler
        assert root.handlers[0].formatter is not None
        assert root.handlers[0].formatter._fmt == updated_format
