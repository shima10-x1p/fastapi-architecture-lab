"""core.shared.settings のユニットテスト。"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.shared.settings import Settings, get_settings

APP_SETTING_ENV_VARS = (
    "APP_APP_NAME",
    "APP_ENV",
    "APP_LOG_LEVEL",
    "APP_LOG_FORMAT",
    "APP_DEBUG",
)


@pytest.fixture(autouse=True)
def isolate_settings_resolution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[None]:
    """設定解決に影響する環境とキャッシュをテストごとに隔離する。"""
    for env_name in APP_SETTING_ENV_VARS:
        monkeypatch.delenv(env_name, raising=False)

    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


class TestSettingsInitialization:
    """Settings の生成と値の解決順序を検証する。"""

    @pytest.mark.parametrize(
        ("field_name", "expected"),
        [
            ("app_name", "fastapi-architecture-lab"),
            ("env", "dev"),
            ("log_level", "INFO"),
            ("debug", False),
        ],
    )
    def test_uses_declared_defaults_when_app_env_vars_are_missing(
        self, field_name: str, expected: str | bool
    ) -> None:
        # 準備

        # 実行
        settings = Settings()

        # 検証
        assert getattr(settings, field_name) == expected

    def test_default_log_format_contains_common_logrecord_attributes(self) -> None:
        # 準備

        # 実行
        settings = Settings()

        # 検証
        assert "%(asctime)s" in settings.log_format
        assert "%(levelname)" in settings.log_format
        assert "%(name)s" in settings.log_format
        assert "%(message)s" in settings.log_format

    def test_loads_values_from_dotenv_when_environment_is_missing(
        self, tmp_path: Path
    ) -> None:
        # 準備
        tmp_path.joinpath(".env").write_text(
            "APP_ENV=staging\nAPP_DEBUG=true\n",
            encoding="utf-8",
        )

        # 実行
        settings = Settings()

        # 検証
        assert settings.env == "staging"
        assert settings.debug is True

    def test_environment_variables_override_dotenv_values(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # 準備
        tmp_path.joinpath(".env").write_text(
            "APP_ENV=prod\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("APP_ENV", "staging")

        # 実行
        settings = Settings()

        # 検証
        assert settings.env == "staging"

    @pytest.mark.parametrize(
        ("env_name", "raw_value", "field_name", "expected"),
        [
            ("APP_APP_NAME", "from-env", "app_name", "from-env"),
            ("APP_ENV", "prod", "env", "prod"),
            ("APP_LOG_LEVEL", "DEBUG", "log_level", "DEBUG"),
            (
                "APP_LOG_FORMAT",
                "%(levelname)s | %(message)s",
                "log_format",
                "%(levelname)s | %(message)s",
            ),
            ("APP_DEBUG", "true", "debug", True),
        ],
    )
    def test_allows_app_prefixed_environment_variables_to_override_defaults(
        self,
        monkeypatch: pytest.MonkeyPatch,
        env_name: str,
        raw_value: str,
        field_name: str,
        expected: str | bool,
    ) -> None:
        # 準備
        monkeypatch.setenv(env_name, raw_value)

        # 実行
        settings = Settings()

        # 検証
        assert getattr(settings, field_name) == expected

    def test_ignores_environment_variables_without_app_prefix(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # 準備
        monkeypatch.setenv("ENV", "prod")

        # 実行
        settings = Settings()

        # 検証
        assert settings.env == "dev"

    def test_rejects_unknown_env_values(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # 準備
        monkeypatch.setenv("APP_ENV", "unknown")

        # 実行 / 検証
        with pytest.raises(ValidationError):
            Settings()


class TestGetSettings:
    """get_settings() のキャッシュ挙動を検証する。"""

    def test_returns_cached_instance_while_cache_is_warm(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # 準備
        monkeypatch.setenv("APP_APP_NAME", "first-name")
        first = get_settings()
        monkeypatch.setenv("APP_APP_NAME", "second-name")

        # 実行
        second = get_settings()

        # 検証
        assert second is first
        assert second.app_name == "first-name"

    def test_reloads_settings_after_cache_clear(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # 準備
        monkeypatch.setenv("APP_APP_NAME", "first-name")
        first = get_settings()
        monkeypatch.setenv("APP_APP_NAME", "second-name")
        get_settings.cache_clear()

        # 実行
        second = get_settings()

        # 検証
        assert second is not first
        assert second.app_name == "second-name"
