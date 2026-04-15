"""複数 adapter から再利用する汎用 HTTP クライアント補助。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

_DEFAULT_HEADERS = {"Accept": "application/json"}


def merge_headers(
    base_headers: Mapping[str, str] | None = None,
    extra_headers: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """ベースヘッダへ追加ヘッダを上書きマージする。"""
    merged_headers = dict(base_headers or {})
    merged_headers.update(extra_headers or {})
    return merged_headers


def create_async_client(
    *,
    base_url: str,
    timeout_seconds: float,
    default_headers: Mapping[str, str] | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> httpx.AsyncClient:
    """共通設定済みの `AsyncClient` を生成する。"""
    return httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(timeout_seconds),
        headers=merge_headers(_DEFAULT_HEADERS, default_headers),
        transport=transport,
    )


async def send_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    """共通設定済みクライアントで HTTP リクエストを送る。"""
    return await client.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
    )
