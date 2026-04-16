# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated.apis.favorites_api_base import BaseFavoritesApi
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
from pydantic import Field, field_validator
from typing import Any, Optional
from typing_extensions import Annotated
from uuid import UUID
from generated.models.create_favorite_request import CreateFavoriteRequest
from generated.models.error_response import ErrorResponse
from generated.models.favorite import Favorite
from generated.models.favorite_list_response import FavoriteListResponse
from generated.models.http_validation_error import HTTPValidationError
from generated.models.update_favorite_request import UpdateFavoriteRequest


router = APIRouter()

ns_pkg = generated.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/favorites",
    responses={
        200: {"model": FavoriteListResponse, "description": "お気に入り一覧（ページネーション付き）"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["favorites"],
    summary="お気に入り動画の一覧を取得する",
    response_model_by_alias=True,
)
async def list_favorites(
    limit: Annotated[Optional[Annotated[int, Field(le=100, strict=True, ge=1)]], Field(description="1ページあたりの最大件数")] = Query(20, description="1ページあたりの最大件数", alias="limit", ge=1, le=100),
    offset: Annotated[Optional[Annotated[int, Field(strict=True, ge=0)]], Field(description="取得開始位置")] = Query(0, description="取得開始位置", alias="offset", ge=0),
    x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")] = Header(None, description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 "),
) -> FavoriteListResponse:
    if not BaseFavoritesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFavoritesApi.subclasses[0]().list_favorites(limit, offset, x_request_id)


@router.post(
    "/v1/favorites",
    responses={
        201: {"model": Favorite, "description": "お気に入り追加完了"},
        409: {"model": ErrorResponse, "description": "リソースが既に存在する（重複登録）"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["favorites"],
    summary="お気に入り動画を追加する",
    response_model_by_alias=True,
)
async def add_favorite(
    create_favorite_request: CreateFavoriteRequest = Body(None, description=""),
    x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")] = Header(None, description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 "),
) -> Favorite:
    """クライアントが動画のメタデータを全て送信する。 同一 videoId が既に登録されている場合は 409 を返す。 """
    if not BaseFavoritesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFavoritesApi.subclasses[0]().add_favorite(create_favorite_request, x_request_id)


@router.get(
    "/v1/favorites/{videoId}",
    responses={
        200: {"model": Favorite, "description": "お気に入り詳細"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["favorites"],
    summary="お気に入り動画を取得する",
    response_model_by_alias=True,
)
async def get_favorite(
    videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")] = Path(..., description="YouTube の動画 ID", regex=r"^[a-zA-Z0-9_-]{11}$"),
    x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")] = Header(None, description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 "),
) -> Favorite:
    if not BaseFavoritesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFavoritesApi.subclasses[0]().get_favorite(videoId, x_request_id)


@router.delete(
    "/v1/favorites/{videoId}",
    responses={
        204: {"description": "削除完了"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
    },
    tags=["favorites"],
    summary="お気に入り動画を削除する",
    response_model_by_alias=True,
)
async def delete_favorite(
    videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")] = Path(..., description="YouTube の動画 ID", regex=r"^[a-zA-Z0-9_-]{11}$"),
    x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")] = Header(None, description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 "),
) -> None:
    if not BaseFavoritesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFavoritesApi.subclasses[0]().delete_favorite(videoId, x_request_id)


@router.patch(
    "/v1/favorites/{videoId}",
    responses={
        200: {"model": Favorite, "description": "更新後のお気に入り詳細"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["favorites"],
    summary="お気に入り動画を更新する（memo・tags）",
    response_model_by_alias=True,
)
async def update_favorite(
    videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")] = Path(..., description="YouTube の動画 ID", regex=r"^[a-zA-Z0-9_-]{11}$"),
    update_favorite_request: UpdateFavoriteRequest = Body(None, description=""),
    x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")] = Header(None, description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 "),
) -> Favorite:
    if not BaseFavoritesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFavoritesApi.subclasses[0]().update_favorite(videoId, update_favorite_request, x_request_id)
