"""core.shared.http_client のユニットテスト。"""

import asyncio

import httpx

from core.shared.http_client import create_async_client, merge_headers, send_request


class TestMergeHeaders:
    """merge_headers() のヘッダ統合を検証する。"""

    def test_allows_extra_headers_to_override_base_headers(self) -> None:
        # 準備
        base_headers = {"Accept": "application/json", "X-Base": "1"}
        extra_headers = {"X-Base": "2", "X-Extra": "3"}

        # 実行
        actual = merge_headers(base_headers, extra_headers)

        # 検証
        assert actual == {
            "Accept": "application/json",
            "X-Base": "2",
            "X-Extra": "3",
        }


class TestCreateAsyncClient:
    """create_async_client() の初期設定を検証する。"""

    def test_sets_base_url_timeout_and_default_headers(self) -> None:
        # 準備

        # 実行
        client = create_async_client(
            base_url="https://openlibrary.org",
            timeout_seconds=3.5,
            default_headers={"User-Agent": "test-agent/1.0"},
        )

        # 検証
        assert client.base_url.scheme == "https"
        assert client.base_url.host == "openlibrary.org"
        assert client.timeout.connect == 3.5
        assert client.headers["Accept"] == "application/json"
        assert client.headers["User-Agent"] == "test-agent/1.0"

        asyncio.run(client.aclose())


class TestSendRequest:
    """send_request() の委譲を検証する。"""

    def test_passes_params_and_headers_to_httpx_client(self) -> None:
        # 準備
        captured_request: httpx.Request | None = None

        async def handler(request: httpx.Request) -> httpx.Response:
            nonlocal captured_request
            captured_request = request
            return httpx.Response(status_code=200, json={"ok": True})

        async def run_test() -> None:
            client = create_async_client(
                base_url="https://openlibrary.org",
                timeout_seconds=5.0,
                transport=httpx.MockTransport(handler),
            )
            try:
                response = await send_request(
                    client,
                    method="GET",
                    url="/search.json",
                    params={"q": "python"},
                    headers={"X-Test": "1"},
                )
            finally:
                await client.aclose()

            assert response.status_code == 200

        # 実行
        asyncio.run(run_test())

        # 検証
        assert captured_request is not None
        assert captured_request.url.path == "/search.json"
        assert captured_request.url.params["q"] == "python"
        assert captured_request.headers["X-Test"] == "1"
