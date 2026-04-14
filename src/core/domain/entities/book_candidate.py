"""Open Library 検索結果を表現するドメインエンティティ。"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.value_objects.open_library_key import OpenLibraryKey


class BookCandidate(BaseModel):
    """検索候補として返す書籍情報。"""

    model_config = ConfigDict(frozen=True)

    open_library_key: OpenLibraryKey
    title: str
    authors: list[str] = Field(min_length=1)
    isbn: str | None = None
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """タイトルが空文字でないことを保証する。"""
        if not value.strip():
            raise ValueError("タイトルは1文字以上である必要があります。")
        return value

    @field_validator("authors")
    @classmethod
    def validate_authors(cls, value: list[str]) -> list[str]:
        """著者配列の妥当性を保証する。"""
        if not value:
            raise ValueError("著者は1件以上必要です。")
        if any(not author.strip() for author in value):
            raise ValueError("著者名に空文字を含めることはできません。")
        return value
