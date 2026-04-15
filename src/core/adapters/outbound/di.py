"""outbound adapter を束ねる dishka provider。"""

from __future__ import annotations

from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide

from core.adapters.outbound.open_library.cache import OpenLibraryCache
from core.adapters.outbound.open_library.catalog_adapter import (
    OpenLibraryCatalogAdapter,
)
from core.application.ports.outbound.open_library_catalog_port import (
    OpenLibraryCatalogPort,
)
from core.shared.http_client import create_async_client
from core.shared.settings import Settings, get_settings


class OutboundAdapterProvider(Provider):
    """HTTP クライアントと outbound adapter を提供する。"""

    @provide(scope=Scope.APP)
    def provide_settings(self) -> Settings:
        """共有 Settings を APP スコープで提供する。"""
        return get_settings()

    @provide(scope=Scope.APP)
    async def provide_open_library_http_client(
        self, settings: Settings
    ) -> AsyncIterable[httpx.AsyncClient]:
        """Open Library 向けの共有 `AsyncClient` を提供する。"""
        client = create_async_client(
            base_url=settings.open_library_base_url,
            timeout_seconds=settings.open_library_timeout_seconds,
            default_headers={
                "User-Agent": settings.open_library_identifying_user_agent,
            },
        )
        try:
            yield client
        finally:
            await client.aclose()

    @provide(scope=Scope.APP)
    def provide_open_library_cache(self, settings: Settings) -> OpenLibraryCache:
        """Open Library 用の APP スコープ cache を提供する。"""
        return OpenLibraryCache(
            ttl_seconds=settings.open_library_cache_ttl_seconds
        )

    @provide(scope=Scope.APP)
    def provide_open_library_catalog_port(
        self,
        settings: Settings,
        http_client: httpx.AsyncClient,
        cache: OpenLibraryCache,
    ) -> OpenLibraryCatalogPort:
        """Open Library port を concrete adapter でバインドする。"""
        return OpenLibraryCatalogAdapter(
            settings=settings,
            http_client=http_client,
            cache=cache,
        )
