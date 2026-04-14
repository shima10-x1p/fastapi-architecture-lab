"""Open Library から取得する詳細メタデータ。"""

from __future__ import annotations

from core.domain.entities.book_candidate import BookCandidate


class BookMetadata(BookCandidate):
    """import / refresh で利用する書誌メタデータ。"""

    description: str | None = None
