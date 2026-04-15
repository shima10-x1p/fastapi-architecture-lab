"""core.adapters.outbound.open_library.catalog_adapter のユニットテスト。"""

import asyncio

import httpx
import pytest

from core.adapters.outbound.open_library.cache import OpenLibraryCache
from core.adapters.outbound.open_library.catalog_adapter import (
    OpenLibraryCatalogAdapter,
)
from core.adapters.outbound.open_library.exceptions import (
    OpenLibraryNotFoundError,
    OpenLibraryRateLimitError,
    OpenLibraryTransportError,
)
from core.domain.entities.book_candidate import BookCandidate
from core.domain.value_objects.book_metadata import BookMetadata
from core.domain.value_objects.open_library_key import OpenLibraryKey
from core.shared.http_client import create_async_client
from core.shared.settings import Settings


def _make_settings() -> Settings:
    """adapter テスト用の Settings を生成する。"""
    return Settings.model_validate(
        {
            "app_name": "fastapi-architecture-lab",
            "env": "dev",
            "log_level": "INFO",
            "log_format": "%(levelname)s %(message)s",
            "debug": False,
            "open_library_base_url": "https://openlibrary.org",
            "open_library_timeout_seconds": 5.0,
            "open_library_user_agent": "fastapi-architecture-lab/0.1.0",
            "open_library_contact_email": "test@example.com",
            "open_library_cache_ttl_seconds": 300,
        }
    )


def _make_adapter(
    handler: httpx.MockTransport,
    *,
    cache: OpenLibraryCache | None = None,
) -> tuple[OpenLibraryCatalogAdapter, httpx.AsyncClient]:
    """MockTransport 付き adapter を生成する。"""
    client = create_async_client(
        base_url="https://openlibrary.org",
        timeout_seconds=5.0,
        default_headers={"User-Agent": "test-agent/1.0"},
        transport=handler,
    )
    adapter = OpenLibraryCatalogAdapter(
        settings=_make_settings(),
        http_client=client,
        cache=cache or OpenLibraryCache(ttl_seconds=300),
    )
    return adapter, client


class TestSearchBookCandidates:
    """search_book_candidates() の挙動を検証する。"""

    def test_uses_cache_before_sending_http_request(self) -> None:
        # 準備
        cache = OpenLibraryCache(ttl_seconds=300)
        cached_candidates = [
            BookCandidate(
                open_library_key=OpenLibraryKey.from_raw("/works/OL19809141W"),
                title="Clean Architecture",
                authors=["Robert C. Martin"],
            )
        ]
        cache.set_search_candidates("python", cached_candidates)

        async def handler(_: httpx.Request) -> httpx.Response:
            raise AssertionError("キャッシュヒット時は HTTP リクエストしない想定です。")

        adapter, client = _make_adapter(
            httpx.MockTransport(handler), cache=cache
        )

        async def run_test() -> None:
            try:
                actual = await adapter.search_book_candidates("python")
            finally:
                await client.aclose()

            assert actual == cached_candidates

        # 実行 / 検証
        asyncio.run(run_test())

    def test_fetches_and_caches_search_results(self) -> None:
        # 準備
        requests: list[str] = []

        async def handler(request: httpx.Request) -> httpx.Response:
            requests.append(str(request.url))
            return httpx.Response(
                status_code=200,
                json={
                    "docs": [
                        {
                            "key": "/works/OL19809141W",
                            "title": "Clean Architecture",
                            "author_name": ["Robert C. Martin"],
                        }
                    ]
                },
            )

        adapter, client = _make_adapter(httpx.MockTransport(handler))

        async def run_test() -> None:
            try:
                first = await adapter.search_book_candidates("python")
                second = await adapter.search_book_candidates("python")
            finally:
                await client.aclose()

            assert len(first) == 1
            assert second == first

        # 実行
        asyncio.run(run_test())

        # 検証
        assert len(requests) == 1

    def test_raises_rate_limit_error_on_429_response(self) -> None:
        # 準備
        async def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=429, json={"detail": "slow down"})

        adapter, client = _make_adapter(httpx.MockTransport(handler))

        async def run_test() -> None:
            try:
                with pytest.raises(OpenLibraryRateLimitError):
                    await adapter.search_book_candidates("python")
            finally:
                await client.aclose()

        # 実行 / 検証
        asyncio.run(run_test())

    def test_raises_transport_error_on_timeout(self) -> None:
        # 準備
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectTimeout("timeout", request=request)

        adapter, client = _make_adapter(httpx.MockTransport(handler))

        async def run_test() -> None:
            try:
                with pytest.raises(OpenLibraryTransportError):
                    await adapter.search_book_candidates("python")
            finally:
                await client.aclose()

        # 実行 / 検証
        asyncio.run(run_test())


class TestFetchBookMetadata:
    """fetch_book_metadata() の挙動を検証する。"""

    def test_fetches_work_authors_and_editions_then_caches_result(self) -> None:
        # 準備
        requests: list[str] = []

        async def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request.url.path)
            if request.url.path == "/works/OL19809141W.json":
                return httpx.Response(
                    status_code=200,
                    json={
                        "key": "/works/OL19809141W",
                        "title": "Clean Architecture",
                        "authors": [{"author": {"key": "/authors/OL2653686A"}}],
                    },
                )
            if request.url.path == "/authors/OL2653686A.json":
                return httpx.Response(
                    status_code=200,
                    json={"name": "Robert C. Martin"},
                )
            if request.url.path == "/works/OL19809141W/editions.json":
                return httpx.Response(
                    status_code=200,
                    json={
                        "entries": [
                            {
                                "isbn_13": ["9780134494166"],
                                "publishers": ["Prentice Hall"],
                                "covers": [8605114],
                                "publish_date": "2017",
                            }
                        ]
                    },
                )
            raise AssertionError(f"想定外のパスです: {request.url.path}")

        adapter, client = _make_adapter(httpx.MockTransport(handler))
        open_library_key = OpenLibraryKey.from_raw("/works/OL19809141W")

        async def run_test() -> BookMetadata:
            try:
                first = await adapter.fetch_book_metadata(open_library_key)
                second = await adapter.fetch_book_metadata(open_library_key)
            finally:
                await client.aclose()

            assert second == first
            return first

        # 実行
        actual = asyncio.run(run_test())

        # 検証
        assert actual.title == "Clean Architecture"
        assert actual.authors == ["Robert C. Martin"]
        assert len(requests) == 3

    def test_raises_not_found_error_on_404_response(self) -> None:
        # 準備
        async def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=404, json={"detail": "not found"})

        adapter, client = _make_adapter(httpx.MockTransport(handler))

        async def run_test() -> None:
            try:
                with pytest.raises(OpenLibraryNotFoundError):
                    await adapter.fetch_book_metadata(
                        OpenLibraryKey.from_raw("/works/OL19809141W")
                    )
            finally:
                await client.aclose()

        # 実行 / 検証
        asyncio.run(run_test())
