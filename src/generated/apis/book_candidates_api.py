# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated.apis.book_candidates_api_base import BaseBookCandidatesApi
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
from typing_extensions import Annotated
from generated.models.book_candidate_list_response import BookCandidateListResponse
from generated.models.http_validation_error import HTTPValidationError


router = APIRouter()

ns_pkg = generated.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/book-candidates",
    responses={
        200: {"model": BookCandidateListResponse, "description": "検索結果の書籍候補一覧"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["book-candidates"],
    summary="外部書誌を検索する",
    response_model_by_alias=True,
)
async def search_book_candidates(
    q: Annotated[str, Field(min_length=1, strict=True, description="検索キーワード（タイトル・著者名など）")] = Query(None, description="検索キーワード（タイトル・著者名など）", alias="q", min_length=1),
) -> BookCandidateListResponse:
    """Open Library の Search API を経由して書籍候補を返す。 結果はキャッシュされる（同一クエリの重複リクエストを抑制するため）。 """
    if not BaseBookCandidatesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBookCandidatesApi.subclasses[0]().search_book_candidates(q)
