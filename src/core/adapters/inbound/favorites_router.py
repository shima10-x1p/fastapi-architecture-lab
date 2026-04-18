"""favorites 用の FastAPI inbound adapter。"""

from __future__ import annotations

from typing import Annotated, NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, status

from core.application.exceptions import AlreadyExistsError, NotFoundError
from core.application.usecases.add_favorite import AddFavoriteInput, AddFavoriteUsecase
from core.application.usecases.get_favorite import GetFavoriteUsecase
from core.application.usecases.list_favorites import (
    ListFavoritesResult,
    ListFavoritesUsecase,
)
from core.domain.favorite import FavoriteEntity
from core.shared.dependencies import (
    get_add_favorite_usecase,
    get_get_favorite_usecase,
    get_list_favorites_usecase,
)
from generated.models.create_favorite_request import CreateFavoriteRequest
from generated.models.error_response import ErrorResponse
from generated.models.favorite import Favorite
from generated.models.favorite_list_response import FavoriteListResponse
from generated.models.http_validation_error import HTTPValidationError

_VIDEO_ID_PATTERN = r"^[a-zA-Z0-9_-]{11}$"

router = APIRouter(prefix="/v1", tags=["favorites"])

type AddFavoriteUsecaseDependency = Annotated[
    AddFavoriteUsecase,
    Depends(get_add_favorite_usecase),
]
type GetFavoriteUsecaseDependency = Annotated[
    GetFavoriteUsecase,
    Depends(get_get_favorite_usecase),
]
type ListFavoritesUsecaseDependency = Annotated[
    ListFavoritesUsecase,
    Depends(get_list_favorites_usecase),
]
type RequestIdHeader = Annotated[
    UUID | None,
    Header(
        alias="X-Request-Id",
        description=(
            "クライアントが任意に設定するトレースID。"
            "ログへの記録やリクエスト追跡に使用する。"
            "省略時はサーバー側で UUID を自動生成する。"
        ),
    ),
]


def _to_response(entity: FavoriteEntity) -> Favorite:
    """
    domain entity を API response model へ変換する。

    Args:
        entity (FavoriteEntity): 変換対象のお気に入り。

    Returns:
        Favorite: API 返却用モデル。
    """

    return Favorite(
        videoId=entity.video_id,
        title=entity.title,
        channelName=entity.channel_name,
        thumbnailUrl=entity.thumbnail_url,
        memo=entity.memo,
        tags=entity.tags,
        createdAt=entity.created_at,
        updatedAt=entity.updated_at,
    )


def _to_list_response(
    result: ListFavoritesResult,
    *,
    limit: int,
    offset: int,
) -> FavoriteListResponse:
    """
    一覧取得結果を API response model へ変換する。

    Args:
        result (ListFavoritesResult): usecase の実行結果。
        limit (int): 取得件数。
        offset (int): 取得開始位置。

    Returns:
        FavoriteListResponse: API 返却用モデル。
    """

    return FavoriteListResponse(
        items=[_to_response(item) for item in result.items],
        total=result.total,
        limit=limit,
        offset=offset,
    )


def _raise_conflict(detail: str) -> NoReturn:
    """409 Conflict を送出する。"""

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
    )


def _raise_not_found(detail: str) -> NoReturn:
    """404 Not Found を送出する。"""

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


@router.get(
    "/favorites",
    operation_id="listFavorites",
    summary="お気に入り動画の一覧を取得する",
    response_model=FavoriteListResponse,
    response_model_by_alias=True,
    responses={
        status.HTTP_200_OK: {
            "model": FavoriteListResponse,
            "description": "お気に入り一覧（ページネーション付き）",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": HTTPValidationError,
            "description": (
                "リクエストの形式・バリデーションエラー"
                "（FastAPI デフォルト）"
            ),
        },
    },
)
async def list_favorites(
    *,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="1ページあたりの最大件数",
        ),
    ] = 20,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description="取得開始位置",
        ),
    ] = 0,
    usecase: ListFavoritesUsecaseDependency,
    x_request_id: RequestIdHeader = None,
) -> FavoriteListResponse:
    """お気に入り一覧を返す。"""

    del x_request_id

    result = await usecase.execute(limit=limit, offset=offset)
    return _to_list_response(result, limit=limit, offset=offset)


@router.post(
    "/favorites",
    operation_id="addFavorite",
    summary="お気に入り動画を追加する",
    description=(
        "クライアントが動画のメタデータを全て送信する。"
        "同一 videoId が既に登録されている場合は 409 を返す。"
    ),
    status_code=status.HTTP_201_CREATED,
    response_model=Favorite,
    response_model_by_alias=True,
    responses={
        status.HTTP_201_CREATED: {
            "model": Favorite,
            "description": "お気に入り追加完了",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "リソースが既に存在する（重複登録）",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": HTTPValidationError,
            "description": (
                "リクエストの形式・バリデーションエラー"
                "（FastAPI デフォルト）"
            ),
        },
    },
)
async def add_favorite(
    request: CreateFavoriteRequest,
    usecase: AddFavoriteUsecaseDependency,
    x_request_id: RequestIdHeader = None,
) -> Favorite:
    """お気に入り動画を追加して返す。"""

    del x_request_id

    try:
        entity = await usecase.execute(
            AddFavoriteInput(
                video_id=request.video_id,
                title=request.title,
                channel_name=request.channel_name,
                thumbnail_url=request.thumbnail_url,
                memo=request.memo,
                tags=request.tags,
            )
        )
    except AlreadyExistsError as exc:
        _raise_conflict(exc.detail)

    return _to_response(entity)


@router.get(
    "/favorites/{videoId}",
    operation_id="getFavorite",
    summary="お気に入り動画を取得する",
    response_model=Favorite,
    response_model_by_alias=True,
    responses={
        status.HTTP_200_OK: {
            "model": Favorite,
            "description": "お気に入り詳細",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "指定されたリソースが存在しない",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": HTTPValidationError,
            "description": (
                "リクエストの形式・バリデーションエラー"
                "（FastAPI デフォルト）"
            ),
        },
    },
)
async def get_favorite(
    video_id: Annotated[
        str,
        Path(
            alias="videoId",
            pattern=_VIDEO_ID_PATTERN,
            description="YouTube の動画 ID",
        ),
    ],
    usecase: GetFavoriteUsecaseDependency,
    x_request_id: RequestIdHeader = None,
) -> Favorite:
    """動画 ID でお気に入りを 1 件返す。"""

    del x_request_id

    try:
        entity = await usecase.execute(video_id)
    except NotFoundError as exc:
        _raise_not_found(exc.detail)

    return _to_response(entity)
