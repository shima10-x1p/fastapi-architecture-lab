# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated.apis.embed_api_base import BaseEmbedApi
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
from pydantic import Field, StrictBool, field_validator
from typing import Optional
from typing_extensions import Annotated
from uuid import UUID
from generated.models.embed_response import EmbedResponse
from generated.models.error_response import ErrorResponse
from generated.models.http_validation_error import HTTPValidationError


router = APIRouter()

ns_pkg = generated.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/favorites/{videoId}/embed",
    responses={
        200: {"model": EmbedResponse, "description": "埋め込み HTML"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["embed"],
    summary="埋め込みプレイヤーの HTML スニペットを取得する",
    response_model_by_alias=True,
)
async def get_embed_player(
    videoId: Annotated[str, Field(strict=True, description="YouTube の動画 ID")] = Path(..., description="YouTube の動画 ID", regex=r"^[a-zA-Z0-9_-]{11}$"),
    width: Annotated[Optional[Annotated[int, Field(le=1920, strict=True, ge=200)]], Field(description="埋め込みプレイヤーの幅（px）")] = Query(560, description="埋め込みプレイヤーの幅（px）", alias="width", ge=200, le=1920),
    height: Annotated[Optional[Annotated[int, Field(le=1080, strict=True, ge=113)]], Field(description="埋め込みプレイヤーの高さ（px）")] = Query(315, description="埋め込みプレイヤーの高さ（px）", alias="height", ge=113, le=1080),
    autoplay: Annotated[Optional[StrictBool], Field(description="自動再生を有効にするか")] = Query(False, description="自動再生を有効にするか", alias="autoplay"),
    x_request_id: Annotated[Optional[UUID], Field(description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 ")] = Header(None, description="クライアントが任意に設定するトレースID。 ログへの記録やリクエスト追跡に使用する。 省略時はサーバー側で UUID を自動生成する。 "),
) -> EmbedResponse:
    """指定したお気に入り動画の &#x60;&lt;iframe&gt;&#x60; 埋め込み HTML を返す。 width / height / autoplay をクエリパラメータでカスタマイズできる。 """
    if not BaseEmbedApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseEmbedApi.subclasses[0]().get_embed_player(videoId, width, height, autoplay, x_request_id)
