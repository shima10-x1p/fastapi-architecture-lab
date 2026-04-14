"""書籍候補検索ユースケース。"""

from __future__ import annotations

from core.application.exceptions import InvalidSearchQueryError
from core.application.ports.outbound.open_library_catalog_port import (
    OpenLibraryCatalogPort,
)
from core.domain.entities.book_candidate import BookCandidate


class SearchBookCandidatesUsecase:
    """Open Library 検索のアプリケーションサービス。"""

    def __init__(self, catalog_port: OpenLibraryCatalogPort) -> None:
        self._catalog_port = catalog_port

    async def execute(self, query: str) -> list[BookCandidate]:
        """検索語を正規化して候補一覧を取得する。"""
        normalized_query = query.strip()
        if not normalized_query:
            raise InvalidSearchQueryError(
                "検索クエリは1文字以上で指定してください。"
            )

        return await self._catalog_port.search_book_candidates(normalized_query)
