# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Optional
from typing_extensions import Annotated
from uuid import UUID
from generated.models.book import Book
from generated.models.book_list_response import BookListResponse
from generated.models.error_response import ErrorResponse
from generated.models.http_validation_error import HTTPValidationError
from generated.models.import_book_request import ImportBookRequest
from generated.models.reading_status import ReadingStatus
from generated.models.update_book_request import UpdateBookRequest


class BaseBooksApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseBooksApi.subclasses = BaseBooksApi.subclasses + (cls,)
    async def list_books(
        self,
        status: Annotated[Optional[ReadingStatus], Field(description="読書状態でフィルタリング")],
        limit: Annotated[Optional[Annotated[int, Field(le=100, strict=True, ge=1)]], Field(description="1ページあたりの最大件数")],
        offset: Annotated[Optional[Annotated[int, Field(strict=True, ge=0)]], Field(description="取得開始位置")],
    ) -> BookListResponse:
        ...


    async def import_book(
        self,
        import_book_request: ImportBookRequest,
    ) -> Book:
        """Open Library のキーを指定して書籍を取り込む。 既に取り込み済みの場合は 409 を返す。 """
        ...


    async def get_book(
        self,
        bookId: Annotated[UUID, Field(description="書籍の UUID")],
    ) -> Book:
        ...


    async def update_book(
        self,
        bookId: Annotated[UUID, Field(description="書籍の UUID")],
        update_book_request: UpdateBookRequest,
    ) -> Book:
        ...


    async def refresh_book_metadata(
        self,
        bookId: Annotated[UUID, Field(description="書籍の UUID")],
    ) -> Book:
        """書籍の著者・出版社・説明文などを Open Library から最新情報で上書きする。 カバー画像 URL も更新される。 """
        ...
