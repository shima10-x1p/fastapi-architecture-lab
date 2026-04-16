"""共有設定ユーティリティの unit test。"""

from collections.abc import Iterator

import pytest
from pydantic import ValidationError

from core.shared.dependencies import clear_settings_cache, get_settings
from core.shared.settings import AppSettings


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Iterator[None]:
    """各テストの前後で設定キャッシュを初期化する。"""

    clear_settings_cache()
    yield
    clear_settings_cache()


def test_app_settings_uses_defaults_when_environment_variables_are_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """環境変数未設定時は既定値を採用する。"""

    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("APP_DEBUG", raising=False)

    settings = AppSettings()

    assert settings.app_name == "fastapi-architecture-lab API"
    assert settings.app_env == "development"
    assert settings.debug is False


def test_get_settings_reads_values_from_os_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OS 環境変数から設定値を読み込める。"""

    monkeypatch.setenv("APP_NAME", "favorite-api")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DEBUG", "true")

    settings = get_settings()

    assert settings.app_name == "favorite-api"
    assert settings.app_env == "test"
    assert settings.debug is True


def test_app_settings_rejects_empty_app_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """空文字のアプリ名は不正値として扱う。"""

    monkeypatch.setenv("APP_NAME", "")
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("APP_DEBUG", raising=False)

    with pytest.raises(ValidationError):
        AppSettings()


def test_get_settings_cache_can_be_cleared_for_reloading(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """設定キャッシュを破棄すると再読込できる。"""

    monkeypatch.setenv("APP_NAME", "first-api")
    first_settings = get_settings()

    monkeypatch.setenv("APP_NAME", "second-api")
    second_settings = get_settings()

    assert second_settings is first_settings
    assert second_settings.app_name == "first-api"

    clear_settings_cache()
    reloaded_settings = get_settings()

    assert reloaded_settings is not first_settings
    assert reloaded_settings.app_name == "second-api"
