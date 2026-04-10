# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated.apis.books_api_base import BaseBooksApi
import generated.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from generated.models.extra_models import TokenModel  # noqa: F401
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


router = APIRouter()

ns_pkg = generated.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/books",
    responses={
        200: {"model": BookListResponse, "description": "書籍一覧（ページネーション付き）"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["books"],
    summary="取り込み済み書籍の一覧を取得する",
    response_model_by_alias=True,
)
async def list_books(
    status: Annotated[Optional[ReadingStatus], Field(description="読書状態でフィルタリング")] = Query(None, description="読書状態でフィルタリング", alias="status"),
    limit: Annotated[Optional[Annotated[int, Field(le=100, strict=True, ge=1)]], Field(description="1ページあたりの最大件数")] = Query(20, description="1ページあたりの最大件数", alias="limit", ge=1, le=100),
    offset: Annotated[Optional[Annotated[int, Field(strict=True, ge=0)]], Field(description="取得開始位置")] = Query(0, description="取得開始位置", alias="offset", ge=0),
) -> BookListResponse:
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().list_books(status, limit, offset)


@router.post(
    "/v1/books/import",
    responses={
        201: {"model": Book, "description": "取り込み完了"},
        409: {"model": ErrorResponse, "description": "リソースが既に存在する（重複取り込みなど）"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["books"],
    summary="外部書誌を取り込む",
    response_model_by_alias=True,
)
async def import_book(
    import_book_request: ImportBookRequest = Body(None, description=""),
) -> Book:
    """Open Library のキーを指定して書籍を取り込む。 既に取り込み済みの場合は 409 を返す。 """
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().import_book(import_book_request)


@router.get(
    "/v1/books/{bookId}",
    responses={
        200: {"model": Book, "description": "書籍詳細"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["books"],
    summary="書籍の詳細を取得する",
    response_model_by_alias=True,
)
async def get_book(
    bookId: Annotated[UUID, Field(description="書籍の UUID")] = Path(..., description="書籍の UUID"),
) -> Book:
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().get_book(bookId)


@router.patch(
    "/v1/books/{bookId}",
    responses={
        200: {"model": Book, "description": "更新後の書籍詳細"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["books"],
    summary="読書状態を更新する",
    response_model_by_alias=True,
)
async def update_book(
    bookId: Annotated[UUID, Field(description="書籍の UUID")] = Path(..., description="書籍の UUID"),
    update_book_request: UpdateBookRequest = Body(None, description=""),
) -> Book:
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().update_book(bookId, update_book_request)


@router.post(
    "/v1/books/{bookId}/metadata:refresh",
    responses={
        200: {"model": Book, "description": "メタデータ更新後の書籍詳細"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["books"],
    summary="Open Library から書籍のメタデータを再取得する",
    response_model_by_alias=True,
)
async def refresh_book_metadata(
    bookId: Annotated[UUID, Field(description="書籍の UUID")] = Path(..., description="書籍の UUID"),
) -> Book:
    """書籍の著者・出版社・説明文などを Open Library から最新情報で上書きする。 カバー画像 URL も更新される。 """
    if not BaseBooksApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBooksApi.subclasses[0]().refresh_book_metadata(bookId)
