"""Open Library payload を内部モデルへ変換する関数群。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.adapters.outbound.open_library.exceptions import OpenLibraryPayloadError
from core.domain.entities.book_candidate import BookCandidate
from core.domain.exceptions import InvalidOpenLibraryKeyError
from core.domain.value_objects.book_metadata import BookMetadata
from core.domain.value_objects.open_library_key import OpenLibraryKey

_COVER_BASE_URL = "https://covers.openlibrary.org/b/id"


def build_cover_url(
    cover_id: int | str | None, *, size: str = "M"
) -> str | None:
    """Cover ID から covers API の URL を生成する。"""
    if cover_id is None:
        return None
    return f"{_COVER_BASE_URL}/{cover_id}-{size}.jpg"


def map_search_payload(payload: Mapping[str, Any]) -> list[BookCandidate]:
    """search.json の payload を検索候補一覧へ変換する。"""
    documents = payload.get("docs")
    if not isinstance(documents, list):
        raise OpenLibraryPayloadError(
            "Open Library の検索レスポンスに docs 配列がありません。"
        )

    candidates: list[BookCandidate] = []
    for document in documents:
        if not isinstance(document, Mapping):
            continue

        try:
            candidates.append(map_search_document(document))
        except OpenLibraryPayloadError:
            continue

    return candidates


def map_search_document(document: Mapping[str, Any]) -> BookCandidate:
    """検索レスポンスの 1 doc を `BookCandidate` へ変換する。"""
    raw_key = _require_non_empty_string(document.get("key"), "key")
    title = _require_non_empty_string(document.get("title"), "title")
    authors = _extract_non_empty_strings(document.get("author_name"))
    if not authors:
        raise OpenLibraryPayloadError("検索結果に著者情報がありません。")

    try:
        open_library_key = OpenLibraryKey.from_raw(raw_key)
    except InvalidOpenLibraryKeyError as exc:
        raise OpenLibraryPayloadError("検索結果の Work キーが不正です。") from exc

    return BookCandidate(
        open_library_key=open_library_key,
        title=title,
        authors=authors,
        isbn=_first_non_empty_string(document.get("isbn")),
        cover_url=build_cover_url(document.get("cover_i")),
        publisher=_first_non_empty_string(document.get("publisher")),
        published_year=_extract_year(document.get("first_publish_year")),
    )


def extract_author_keys(work_payload: Mapping[str, Any]) -> list[str]:
    """work payload から author key 一覧を抽出する。"""
    authors = work_payload.get("authors")
    if not isinstance(authors, list):
        return []

    author_keys: list[str] = []
    for author_item in authors:
        if not isinstance(author_item, Mapping):
            continue

        raw_author = author_item.get("author")
        if not isinstance(raw_author, Mapping):
            continue

        author_key = raw_author.get("key")
        if isinstance(author_key, str) and author_key.strip():
            author_keys.append(author_key.strip())

    return author_keys


def select_best_edition(
    editions_payload: Mapping[str, Any], *, max_candidates: int = 5
) -> Mapping[str, Any] | None:
    """情報量が多い edition を優先して 1 件選ぶ。"""
    entries = editions_payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return None

    candidates = [
        entry for entry in entries[:max_candidates] if isinstance(entry, Mapping)
    ]
    if not candidates:
        return None

    _, selected_edition = max(
        enumerate(candidates),
        key=lambda item: (_score_edition(item[1]), -item[0]),
    )
    return selected_edition


def map_book_metadata(
    *,
    work_payload: Mapping[str, Any],
    author_payloads: Sequence[Mapping[str, Any]],
    editions_payload: Mapping[str, Any],
) -> BookMetadata:
    """work / author / editions payload を統合して `BookMetadata` を作る。"""
    raw_key = _require_non_empty_string(work_payload.get("key"), "key")
    title = _require_non_empty_string(work_payload.get("title"), "title")

    try:
        open_library_key = OpenLibraryKey.from_raw(raw_key)
    except InvalidOpenLibraryKeyError as exc:
        raise OpenLibraryPayloadError("work payload の key が不正です。") from exc

    authors = [
        author_name
        for author_payload in author_payloads
        if (author_name := _optional_non_empty_string(author_payload.get("name")))
        is not None
    ]
    if not authors:
        raise OpenLibraryPayloadError("著者名を解決できませんでした。")

    best_edition = select_best_edition(editions_payload)
    isbn = None
    cover_url = build_cover_url(_first_cover_id(work_payload.get("covers")))
    publisher = None
    published_year = _extract_year(work_payload.get("first_publish_date"))

    if best_edition is not None:
        isbn = _first_non_empty_string(best_edition.get("isbn_13")) or (
            _first_non_empty_string(best_edition.get("isbn_10"))
        )
        publisher = _first_non_empty_string(best_edition.get("publishers"))
        published_year = _extract_year(best_edition.get("publish_date")) or (
            published_year
        )
        cover_url = build_cover_url(_first_cover_id(best_edition.get("covers"))) or (
            cover_url
        )

    return BookMetadata(
        open_library_key=open_library_key,
        title=title,
        authors=authors,
        isbn=isbn,
        cover_url=cover_url,
        publisher=publisher,
        published_year=published_year,
        description=_extract_description(work_payload.get("description")),
    )


def _score_edition(edition: Mapping[str, Any]) -> int:
    """edition の情報量を雑にスコアリングする。"""
    score = 0
    if _first_non_empty_string(edition.get("isbn_13")) or _first_non_empty_string(
        edition.get("isbn_10")
    ):
        score += 4
    if _first_non_empty_string(edition.get("publishers")):
        score += 2
    if _first_cover_id(edition.get("covers")) is not None:
        score += 1
    if _extract_year(edition.get("publish_date")) is not None:
        score += 1
    return score


def _extract_description(value: Any) -> str | None:
    """description の揺れを吸収して文字列へ正規化する。"""
    if isinstance(value, str):
        normalized_value = value.strip()
        return normalized_value or None

    if isinstance(value, Mapping):
        raw_text = value.get("value")
        if isinstance(raw_text, str) and raw_text.strip():
            return raw_text.strip()

    return None


def _extract_non_empty_strings(value: Any) -> list[str]:
    """文字列配列らしき値から空でない文字列だけを取り出す。"""
    if not isinstance(value, list):
        return []

    return [
        item.strip()
        for item in value
        if isinstance(item, str) and item.strip()
    ]


def _first_non_empty_string(value: Any) -> str | None:
    """文字列または文字列配列から最初の非空文字列を返す。"""
    if isinstance(value, str) and value.strip():
        return value.strip()

    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()

    return None


def _first_cover_id(value: Any) -> int | str | None:
    """covers 配列から最初の cover id を返す。"""
    if not isinstance(value, list):
        return None

    for item in value:
        if isinstance(item, int | str):
            return item

    return None


def _extract_year(value: Any) -> int | None:
    """publish_date 系の値から 4 桁年を取り出す。"""
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        digits = "".join(character for character in value if character.isdigit())
        if len(digits) >= 4:
            return int(digits[:4])

    return None


def _optional_non_empty_string(value: Any) -> str | None:
    """空でない文字列だけを返し、それ以外は `None` を返す。"""
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _require_non_empty_string(value: Any, field_name: str) -> str:
    """必須の文字列フィールドを検証する。"""
    normalized_value = _optional_non_empty_string(value)
    if normalized_value is None:
        raise OpenLibraryPayloadError(
            f"Open Library レスポンスの {field_name} が不正です。"
        )
    return normalized_value
