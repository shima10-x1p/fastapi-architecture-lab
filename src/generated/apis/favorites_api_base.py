# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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


class BaseFavoritesApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseFavoritesApi.subclasses = BaseFavoritesApi.subclasses + (cls,)
    async def list_favorites(
        self,
        limit: Annotated[Optional[Annotated[int, Field(le=100, strict=True, ge=1)]], Field(description="1ページあたりの最大件数")],
        offset: Annotated[Optional[Annotated[int, Field(strict=True, ge=0)]], Field(description="取得開始位置")],
        x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")],
    ) -> FavoriteListResponse:
        ...


    async def add_favorite(
        self,
        create_favorite_request: CreateFavoriteRequest,
        x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")],
    ) -> Favorite:
        """クライアントが動画のメタデータを全て送信する。 同一 videoId が既に登録されている場合は 409 を返す。 """
        ...


    async def get_favorite(
        self,
        videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")],
        x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")],
    ) -> Favorite:
        ...


    async def delete_favorite(
        self,
        videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")],
        x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")],
    ) -> None:
        ...


    async def update_favorite(
        self,
        videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")],
        update_favorite_request: UpdateFavoriteRequest,
        x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")],
    ) -> Favorite:
        ...
