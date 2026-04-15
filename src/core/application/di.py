"""ユースケースを束ねる dishka provider。"""

from __future__ import annotations

from dishka import Provider, Scope, provide

from core.application.ports.outbound.open_library_catalog_port import (
    OpenLibraryCatalogPort,
)
from core.application.usecases.search_book_candidates import (
    SearchBookCandidatesUsecase,
)


class UsecaseProvider(Provider):
    """request スコープでユースケースを提供する。"""

    @provide(scope=Scope.REQUEST)
    def provide_search_book_candidates_usecase(
        self, catalog_port: OpenLibraryCatalogPort
    ) -> SearchBookCandidatesUsecase:
        """検索ユースケースを提供する。"""
        return SearchBookCandidatesUsecase(catalog_port=catalog_port)
