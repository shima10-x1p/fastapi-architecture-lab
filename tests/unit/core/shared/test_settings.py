"""core.shared.settings のユニットテスト。"""

import pytest

from core.shared.settings import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """各テストを新しい Settings インスタンスから開始させる。"""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestSettingsDefaults:
    """環境変数が未設定でも妥当なデフォルト値を返すこと。"""

    def test_default_app_name(self):
        s = Settings()
        assert s.app_name == "fastapi-architecture-lab"

    def test_default_env(self):
        s = Settings()
        assert s.env == "dev"

    def test_default_log_level(self):
        s = Settings()
        assert s.log_level == "INFO"

    def test_default_log_format_contains_common_attributes(self):
        # デフォルト形式には主要な LogRecord 属性を含める
        s = Settings()
        assert "%(asctime)s" in s.log_format
        assert "%(levelname)" in s.log_format
        assert "%(name)s" in s.log_format
        assert "%(message)s" in s.log_format

    def test_default_debug_is_false(self):
        s = Settings()
        assert s.debug is False


class TestSettingsEnvOverride:
    """環境変数（APP_ プレフィックス）でデフォルトを上書きできること。"""

    def test_override_log_level(self, monkeypatch):
        monkeypatch.setenv("APP_LOG_LEVEL", "DEBUG")
        s = Settings()
        assert s.log_level == "DEBUG"

    def test_override_log_format(self, monkeypatch):
        custom_fmt = "%(levelname)s | %(message)s"
        monkeypatch.setenv("APP_LOG_FORMAT", custom_fmt)
        s = Settings()
        assert s.log_format == custom_fmt

    def test_override_env(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "prod")
        s = Settings()
        assert s.env == "prod"

    def test_override_debug(self, monkeypatch):
        monkeypatch.setenv("APP_DEBUG", "true")
        s = Settings()
        assert s.debug is True

    def test_invalid_env_value_raises(self, monkeypatch):
        from pydantic import ValidationError

        monkeypatch.setenv("APP_ENV", "unknown")
        with pytest.raises(ValidationError):
            Settings()


class TestGetSettings:
    """get_settings() がキャッシュ付きシングルトンを返すこと。"""

    def test_returns_settings_instance(self):
        assert isinstance(get_settings(), Settings)

    def test_same_instance_on_repeated_calls(self):
        assert get_settings() is get_settings()

    def test_cache_clear_creates_new_instance(self, monkeypatch):
        first = get_settings()
        get_settings.cache_clear()
        monkeypatch.setenv("APP_APP_NAME", "new-name")
        second = get_settings()
        assert first is not second
