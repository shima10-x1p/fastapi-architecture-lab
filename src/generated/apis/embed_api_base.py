# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictBool, field_validator
from typing import Optional
from typing_extensions import Annotated
from uuid import UUID
from generated.models.embed_response import EmbedResponse
from generated.models.error_response import ErrorResponse
from generated.models.http_validation_error import HTTPValidationError


class BaseEmbedApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseEmbedApi.subclasses = BaseEmbedApi.subclasses + (cls,)
    async def get_embed_player(
        self,
        videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")],
        width: Annotated[Optional[Annotated[int, Field(le=1920, strict=True, ge=200)]], Field(description="埋め込みプレイヤーの幅（px）")],
        height: Annotated[Optional[Annotated[int, Field(le=1080, strict=True, ge=113)]], Field(description="埋め込みプレイヤーの高さ（px）")],
        autoplay: Annotated[Optional[StrictBool], Field(description="自動再生を有効にするか")],
        x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")],
    ) -> EmbedResponse:
        """指定したお気に入り動画の &#x60;&lt;iframe&gt;&#x60; 埋め込み HTML を返す。 width / height / autoplay をクエリパラメータでカスタマイズできる。 """
        ...
