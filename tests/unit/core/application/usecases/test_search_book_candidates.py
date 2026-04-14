"""core.application.usecases.search_book_candidates のユニットテスト。"""

import asyncio

import pytest

from core.application.exceptions import InvalidSearchQueryError
from core.application.ports.outbound.open_library_catalog_port import (
    OpenLibraryCatalogPort,
)
from core.application.usecases.search_book_candidates import (
    SearchBookCandidatesUsecase,
)
from core.domain.entities.book_candidate import BookCandidate
from core.domain.value_objects.book_metadata import BookMetadata
from core.domain.value_objects.open_library_key import OpenLibraryKey


class _FakeOpenLibraryCatalogPort(OpenLibraryCatalogPort):
    """ユースケース検証用の fake port。"""

    def __init__(self, response: list[BookCandidate]) -> None:
        self.response = response
        self.queries: list[str] = []

    async def search_book_candidates(self, query: str) -> list[BookCandidate]:
        self.queries.append(query)
        return self.response

    async def fetch_book_metadata(
        self, open_library_key: OpenLibraryKey
    ) -> BookMetadata:
        raise AssertionError(
            "SearchBookCandidatesUsecase では fetch_book_metadata は呼ばれない想定です。"
        )


def _make_candidate(title: str = "Clean Architecture") -> BookCandidate:
    """テストで使う BookCandidate を生成する。"""
    return BookCandidate(
        open_library_key=OpenLibraryKey.from_raw("/works/OL19809141W"),
        title=title,
        authors=["Robert C. Martin"],
        isbn="9780134494166",
        cover_url="https://covers.openlibrary.org/b/id/8605114-M.jpg",
        publisher="Prentice Hall",
        published_year=2017,
    )


class TestSearchBookCandidatesUsecase:
    """SearchBookCandidatesUsecase の振る舞いを検証する。"""

    def test_trims_query_before_delegating_to_port(self) -> None:
        # 準備
        expected = [_make_candidate()]
        fake_port = _FakeOpenLibraryCatalogPort(response=expected)
        usecase = SearchBookCandidatesUsecase(catalog_port=fake_port)

        # 実行
        actual = asyncio.run(usecase.execute("  clean architecture  "))

        # 検証
        assert fake_port.queries == ["clean architecture"]
        assert actual == expected

    @pytest.mark.parametrize("query", ["", " ", "\n", "\t"])
    def test_raises_error_when_query_is_blank_after_trim(
        self, query: str
    ) -> None:
        # 準備
        fake_port = _FakeOpenLibraryCatalogPort(response=[_make_candidate()])
        usecase = SearchBookCandidatesUsecase(catalog_port=fake_port)

        # 実行 / 検証
        with pytest.raises(InvalidSearchQueryError):
            asyncio.run(usecase.execute(query))

        assert fake_port.queries == []

    def test_returns_domain_models_without_conversion(self) -> None:
        # 準備
        expected = [_make_candidate(title="Refactoring")]
        fake_port = _FakeOpenLibraryCatalogPort(response=expected)
        usecase = SearchBookCandidatesUsecase(catalog_port=fake_port)

        # 実行
        actual = asyncio.run(usecase.execute("refactoring"))

        # 検証
        assert actual is expected
