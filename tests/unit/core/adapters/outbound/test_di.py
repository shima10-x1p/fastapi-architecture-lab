"""core.adapters.outbound.di のユニットテスト。"""

import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from dishka import make_async_container

from core.adapters.outbound.di import OutboundAdapterProvider
from core.adapters.outbound.open_library.cache import OpenLibraryCache
from core.adapters.outbound.open_library.catalog_adapter import (
    OpenLibraryCatalogAdapter,
)
from core.application.ports.outbound.open_library_catalog_port import (
    OpenLibraryCatalogPort,
)
from core.shared.settings import Settings, get_settings


@pytest.fixture(autouse=True)
def isolate_outbound_provider_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[None]:
    """provider テスト用に settings と cache を隔離する。"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_OPEN_LIBRARY_CONTACT_EMAIL", "test@example.com")
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


class TestOutboundAdapterProvider:
    """OutboundAdapterProvider の解決結果を検証する。"""

    def test_resolves_catalog_port_and_shared_dependencies(self) -> None:
        # 準備

        async def exercise() -> tuple[Settings, OpenLibraryCache, object]:
            container = make_async_container(OutboundAdapterProvider())
            try:
                async with container() as request_container:
                    settings = await request_container.get(Settings)
                    cache = await request_container.get(OpenLibraryCache)
                    catalog_port = await request_container.get(
                        OpenLibraryCatalogPort
                    )
                return settings, cache, catalog_port
            finally:
                await container.close()

        # 実行
        settings, cache, catalog_port = asyncio.run(exercise())

        # 検証
        assert settings.open_library_contact_email == "test@example.com"
        assert isinstance(cache, OpenLibraryCache)
        assert isinstance(catalog_port, OpenLibraryCatalogAdapter)
