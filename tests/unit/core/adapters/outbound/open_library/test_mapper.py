"""core.adapters.outbound.open_library.mapper のユニットテスト。"""

import pytest

from core.adapters.outbound.open_library.exceptions import OpenLibraryPayloadError
from core.adapters.outbound.open_library.mapper import (
    build_cover_url,
    extract_author_keys,
    map_book_metadata,
    map_search_payload,
    select_best_edition,
)


class TestBuildCoverUrl:
    """build_cover_url() の URL 生成を検証する。"""

    def test_returns_cover_url_when_cover_id_exists(self) -> None:
        # 準備

        # 実行
        actual = build_cover_url(8605114)

        # 検証
        assert actual == "https://covers.openlibrary.org/b/id/8605114-M.jpg"

    def test_returns_none_when_cover_id_is_missing(self) -> None:
        # 準備

        # 実行
        actual = build_cover_url(None)

        # 検証
        assert actual is None


class TestMapSearchPayload:
    """search payload の変換を検証する。"""

    def test_maps_valid_search_documents_to_book_candidates(self) -> None:
        # 準備
        payload = {
            "docs": [
                {
                    "key": "/works/OL19809141W",
                    "title": "Clean Architecture",
                    "author_name": ["Robert C. Martin"],
                    "isbn": ["9780134494166"],
                    "publisher": ["Prentice Hall"],
                    "cover_i": 8605114,
                    "first_publish_year": 2017,
                }
            ]
        }

        # 実行
        actual = map_search_payload(payload)

        # 検証
        assert len(actual) == 1
        assert actual[0].title == "Clean Architecture"
        assert actual[0].authors == ["Robert C. Martin"]
        assert actual[0].isbn == "9780134494166"

    def test_skips_invalid_search_documents(self) -> None:
        # 準備
        payload = {
            "docs": [
                {
                    "key": "/works/OL19809141W",
                    "title": "Valid",
                    "author_name": ["A"],
                },
                {
                    "key": "invalid",
                    "title": "Broken",
                    "author_name": ["B"],
                },
            ]
        }

        # 実行
        actual = map_search_payload(payload)

        # 検証
        assert len(actual) == 1
        assert actual[0].title == "Valid"


class TestExtractAuthorKeys:
    """work payload からの author key 抽出を検証する。"""

    def test_extracts_author_keys_from_work_payload(self) -> None:
        # 準備
        work_payload = {
            "authors": [
                {"author": {"key": "/authors/OL1A"}},
                {"author": {"key": "/authors/OL2A"}},
            ]
        }

        # 実行
        actual = extract_author_keys(work_payload)

        # 検証
        assert actual == ["/authors/OL1A", "/authors/OL2A"]


class TestSelectBestEdition:
    """edition 選定ロジックを検証する。"""

    def test_prefers_edition_with_richer_metadata(self) -> None:
        # 準備
        editions_payload = {
            "entries": [
                {"publishers": ["Only Publisher"]},
                {
                    "isbn_13": ["9780134494166"],
                    "publishers": ["Prentice Hall"],
                    "covers": [8605114],
                    "publish_date": "2017",
                },
            ]
        }

        # 実行
        actual = select_best_edition(editions_payload)

        # 検証
        assert actual is not None
        assert actual["publishers"] == ["Prentice Hall"]


class TestMapBookMetadata:
    """複数 payload の統合を検証する。"""

    def test_combines_work_author_and_edition_payloads(self) -> None:
        # 準備
        work_payload = {
            "key": "/works/OL19809141W",
            "title": "Clean Architecture",
            "description": {
                "value": "A craftsman's guide to software structure and design."
            },
            "authors": [{"author": {"key": "/authors/OL2653686A"}}],
            "covers": [8605114],
        }
        author_payloads = [{"name": "Robert C. Martin"}]
        editions_payload = {
            "entries": [
                {
                    "isbn_13": ["9780134494166"],
                    "publishers": ["Prentice Hall"],
                    "covers": [8605114],
                    "publish_date": "2017",
                }
            ]
        }

        # 実行
        actual = map_book_metadata(
            work_payload=work_payload,
            author_payloads=author_payloads,
            editions_payload=editions_payload,
        )

        # 検証
        assert actual.title == "Clean Architecture"
        assert actual.authors == ["Robert C. Martin"]
        assert actual.description == (
            "A craftsman's guide to software structure and design."
        )
        assert actual.publisher == "Prentice Hall"

    def test_raises_error_when_author_names_cannot_be_resolved(self) -> None:
        # 準備
        work_payload = {
            "key": "/works/OL19809141W",
            "title": "Clean Architecture",
        }

        # 実行 / 検証
        with pytest.raises(OpenLibraryPayloadError):
            map_book_metadata(
                work_payload=work_payload,
                author_payloads=[{}],
                editions_payload={"entries": []},
            )
