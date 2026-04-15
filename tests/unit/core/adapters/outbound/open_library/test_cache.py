"""core.adapters.outbound.open_library.cache のユニットテスト。"""

from core.adapters.outbound.open_library.cache import OpenLibraryCache
from core.domain.entities.book_candidate import BookCandidate
from core.domain.value_objects.book_metadata import BookMetadata
from core.domain.value_objects.open_library_key import OpenLibraryKey


class _Clock:
    """テスト用に時刻を手動制御するクロック。"""

    def __init__(self) -> None:
        self.current = 0.0

    def __call__(self) -> float:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += seconds


def _make_candidate() -> BookCandidate:
    """テスト用の BookCandidate を生成する。"""
    return BookCandidate(
        open_library_key=OpenLibraryKey.from_raw("/works/OL19809141W"),
        title="Clean Architecture",
        authors=["Robert C. Martin"],
        isbn="9780134494166",
        cover_url="https://covers.openlibrary.org/b/id/8605114-M.jpg",
        publisher="Prentice Hall",
        published_year=2017,
    )


def _make_metadata() -> BookMetadata:
    """テスト用の BookMetadata を生成する。"""
    return BookMetadata(
        open_library_key=OpenLibraryKey.from_raw("/works/OL19809141W"),
        title="Clean Architecture",
        authors=["Robert C. Martin"],
        isbn="9780134494166",
        cover_url="https://covers.openlibrary.org/b/id/8605114-M.jpg",
        publisher="Prentice Hall",
        published_year=2017,
        description="A craftsman's guide to software structure and design.",
    )


class TestOpenLibraryCache:
    """OpenLibraryCache の TTL 挙動を検証する。"""

    def test_returns_none_for_missing_search_cache(self) -> None:
        # 準備
        cache = OpenLibraryCache(ttl_seconds=60)

        # 実行
        actual = cache.get_search_candidates("python")

        # 検証
        assert actual is None

    def test_returns_cached_search_candidates_before_expiry(self) -> None:
        # 準備
        clock = _Clock()
        cache = OpenLibraryCache(ttl_seconds=60, clock=clock)
        expected = [_make_candidate()]
        cache.set_search_candidates("python", expected)
        clock.advance(30)

        # 実行
        actual = cache.get_search_candidates("python")

        # 検証
        assert actual == expected

    def test_expires_cached_search_candidates_after_ttl(self) -> None:
        # 準備
        clock = _Clock()
        cache = OpenLibraryCache(ttl_seconds=60, clock=clock)
        cache.set_search_candidates("python", [_make_candidate()])
        clock.advance(61)

        # 実行
        actual = cache.get_search_candidates("python")

        # 検証
        assert actual is None

    def test_keeps_search_and_metadata_entries_separate(self) -> None:
        # 準備
        cache = OpenLibraryCache(ttl_seconds=60)
        candidate = _make_candidate()
        metadata = _make_metadata()
        open_library_key = OpenLibraryKey.from_raw("/works/OL19809141W")
        cache.set_search_candidates("python", [candidate])
        cache.set_book_metadata(open_library_key, metadata)

        # 実行
        actual_candidates = cache.get_search_candidates("python")
        actual_metadata = cache.get_book_metadata(open_library_key)

        # 検証
        assert actual_candidates == [candidate]
        assert actual_metadata == metadata
