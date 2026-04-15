"""Open Library の concrete outbound adapter。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from core.adapters.outbound.open_library.cache import OpenLibraryCache
from core.adapters.outbound.open_library.exceptions import (
    OpenLibraryNotFoundError,
    OpenLibraryPayloadError,
    OpenLibraryRateLimitError,
    OpenLibraryTransportError,
)
from core.adapters.outbound.open_library.mapper import (
    extract_author_keys,
    map_book_metadata,
    map_search_payload,
)
from core.application.ports.outbound.open_library_catalog_port import (
    OpenLibraryCatalogPort,
)
from core.domain.entities.book_candidate import BookCandidate
from core.domain.value_objects.book_metadata import BookMetadata
from core.domain.value_objects.open_library_key import OpenLibraryKey
from core.shared.http_client import send_request
from core.shared.settings import Settings


class OpenLibraryCatalogAdapter(OpenLibraryCatalogPort):
    """Open Library API を呼び出す adapter 実装。"""

    def __init__(
        self,
        settings: Settings,
        http_client: httpx.AsyncClient,
        cache: OpenLibraryCache,
    ) -> None:
        self._settings = settings
        self._http_client = http_client
        self._cache = cache

    async def search_book_candidates(self, query: str) -> list[BookCandidate]:
        """検索候補を取得し、結果をキャッシュする。"""
        cached_candidates = self._cache.get_search_candidates(query)
        if cached_candidates is not None:
            return cached_candidates

        payload = await self._get_json("/search.json", params={"q": query})
        candidates = map_search_payload(payload)
        self._cache.set_search_candidates(query, candidates)
        return candidates

    async def fetch_book_metadata(
        self, open_library_key: OpenLibraryKey
    ) -> BookMetadata:
        """書誌詳細を取得し、結果をキャッシュする。"""
        cached_metadata = self._cache.get_book_metadata(open_library_key)
        if cached_metadata is not None:
            return cached_metadata

        work_payload = await self._get_json(f"{open_library_key.value}.json")
        author_keys = extract_author_keys(work_payload)
        author_payloads = [
            await self._get_json(f"{author_key}.json")
            for author_key in author_keys
        ]
        editions_payload = await self._get_json(
            f"{open_library_key.value}/editions.json",
            params={"limit": 5},
        )

        metadata = map_book_metadata(
            work_payload=work_payload,
            author_payloads=author_payloads,
            editions_payload=editions_payload,
        )
        self._cache.set_book_metadata(open_library_key, metadata)
        return metadata

    async def _get_json(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """Open Library から JSON payload を取得して検証する。"""
        try:
            response = await send_request(
                self._http_client,
                method="GET",
                url=path,
                params=params,
            )
        except httpx.TimeoutException as exc:
            raise OpenLibraryTransportError(
                f"Open Library への通信がタイムアウトしました: {self._build_url(path)}"
            ) from exc
        except httpx.RequestError as exc:
            raise OpenLibraryTransportError(
                f"Open Library への通信に失敗しました: {self._build_url(path)}"
            ) from exc

        if response.status_code == httpx.codes.NOT_FOUND:
            raise OpenLibraryNotFoundError(
                f"Open Library に対象リソースが見つかりません: {self._build_url(path)}"
            )
        if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            raise OpenLibraryRateLimitError(
                "Open Library のレート制限に到達しました。"
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise OpenLibraryTransportError(
                f"Open Library がエラーを返しました: {response.status_code}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise OpenLibraryPayloadError(
                f"Open Library の JSON を解釈できません: {self._build_url(path)}"
            ) from exc

        if not isinstance(payload, Mapping):
            raise OpenLibraryPayloadError(
                f"Open Library のレスポンス形式が不正です: {self._build_url(path)}"
            )

        return payload

    def _build_url(self, path: str) -> str:
        """エラーメッセージ用に絶対 URL を組み立てる。"""
        return f"{self._settings.open_library_base_url}{path}"
