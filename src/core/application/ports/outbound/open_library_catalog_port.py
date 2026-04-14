"""Open Library 連携の outbound port 定義。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.domain.entities.book_candidate import BookCandidate
from core.domain.value_objects.book_metadata import BookMetadata
from core.domain.value_objects.open_library_key import OpenLibraryKey


class OpenLibraryCatalogPort(ABC):
    """Open Library カタログ連携の抽象インターフェース。"""

    @abstractmethod
    async def search_book_candidates(self, query: str) -> list[BookCandidate]:
        """検索クエリに一致する書籍候補を返す。"""

    @abstractmethod
    async def fetch_book_metadata(
        self, open_library_key: OpenLibraryKey
    ) -> BookMetadata:
        """指定 Work キーの書誌メタデータを返す。"""
