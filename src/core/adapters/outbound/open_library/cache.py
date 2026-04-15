"""Open Library adapter 内部で使う TTL キャッシュ。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic

from core.domain.entities.book_candidate import BookCandidate
from core.domain.value_objects.book_metadata import BookMetadata
from core.domain.value_objects.open_library_key import OpenLibraryKey


@dataclass(frozen=True, slots=True)
class _CacheEntry[T]:
    """キャッシュ値と期限を束ねる内部エントリ。"""

    value: T
    expires_at: float


class OpenLibraryCache:
    """検索結果とメタデータを保持する process-local キャッシュ。"""

    def __init__(
        self,
        ttl_seconds: int,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._ttl_seconds = float(ttl_seconds)
        self._clock = clock
        self._search_cache: dict[str, _CacheEntry[list[BookCandidate]]] = {}
        self._metadata_cache: dict[str, _CacheEntry[BookMetadata]] = {}

    def get_search_candidates(self, query: str) -> list[BookCandidate] | None:
        """検索結果キャッシュから候補一覧を取得する。"""
        return self._get_entry(self._search_cache, query)

    def set_search_candidates(
        self, query: str, candidates: list[BookCandidate]
    ) -> None:
        """検索結果キャッシュへ候補一覧を保存する。"""
        self._search_cache[query] = _CacheEntry(
            value=candidates,
            expires_at=self._clock() + self._ttl_seconds,
        )

    def get_book_metadata(
        self, open_library_key: OpenLibraryKey
    ) -> BookMetadata | None:
        """書誌メタデータキャッシュから結果を取得する。"""
        return self._get_entry(self._metadata_cache, open_library_key.value)

    def set_book_metadata(
        self, open_library_key: OpenLibraryKey, metadata: BookMetadata
    ) -> None:
        """書誌メタデータキャッシュへ結果を保存する。"""
        self._metadata_cache[open_library_key.value] = _CacheEntry(
            value=metadata,
            expires_at=self._clock() + self._ttl_seconds,
        )

    def _get_entry[T](
        self, store: dict[str, _CacheEntry[T]], key: str
    ) -> T | None:
        """有効期限付きエントリを安全に取得する。"""
        cached_entry = store.get(key)
        if cached_entry is None:
            return None

        if cached_entry.expires_at <= self._clock():
            del store[key]
            return None

        return cached_entry.value
