"""favorites_router の unit test。"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.adapters.inbound.favorites_router import router
from core.application.exceptions import AlreadyExistsError, NotFoundError
from core.application.usecases.add_favorite import AddFavoriteInput
from core.application.usecases.list_favorites import ListFavoritesResult
from core.domain.favorite import FavoriteEntity
from core.shared.dependencies import (
    get_add_favorite_usecase,
    get_get_favorite_usecase,
    get_list_favorites_usecase,
)

_REQUEST_ID = "123e4567-e89b-12d3-a456-426614174000"


def _build_entity(
    *,
    video_id: str = "videoid0001",
    title: str = "お気に入り動画",
    channel_name: str | None = "チャンネル名",
    thumbnail_url: str | None = "https://example.com/thumb.jpg",
    memo: str | None = "あとで見る",
    tags: list[str] | None = None,
) -> FavoriteEntity:
    """テスト用の FavoriteEntity を返す。"""

    if tags is None:
        tags = []

    return FavoriteEntity(
        video_id=video_id,
        title=title,
        channel_name=channel_name,
        thumbnail_url=thumbnail_url,
        memo=memo,
        tags=tags,
        created_at=datetime(2025, 1, 2, 3, 4, 5, tzinfo=UTC),
        updated_at=datetime(2025, 1, 3, 4, 5, 6, tzinfo=UTC),
    )


class ListFavoritesSpyUsecase:
    """一覧取得 usecase の呼び出しを記録するスパイ。"""

    def __init__(self, result: ListFavoritesResult) -> None:
        """返却結果を受け取って初期化する。"""

        self.called_with: tuple[int, int] | None = None
        self._result = result

    async def execute(self, limit: int, offset: int) -> ListFavoritesResult:
        """受け取ったページング条件を記録して結果を返す。"""

        self.called_with = (limit, offset)
        return self._result


class AddFavoriteSpyUsecase:
    """追加 usecase の入力値と戻り値を制御するスパイ。"""

    def __init__(
        self,
        *,
        result: FavoriteEntity | None = None,
        error: Exception | None = None,
    ) -> None:
        """戻り値または例外を切り替えられるように初期化する。"""

        self.received_input: AddFavoriteInput | None = None
        self._result = result
        self._error = error

    async def execute(self, input_data: AddFavoriteInput) -> FavoriteEntity:
        """受け取った入力値を記録し、指定された結果を返す。"""

        self.received_input = input_data
        if self._error is not None:
            raise self._error
        if self._result is not None:
            return self._result

        return _build_entity(
            video_id=input_data.video_id,
            title=input_data.title,
            channel_name=input_data.channel_name,
            thumbnail_url=input_data.thumbnail_url,
            memo=input_data.memo,
            tags=[] if input_data.tags is None else input_data.tags,
        )


class GetFavoriteSpyUsecase:
    """単体取得 usecase の戻り値と例外を制御するスパイ。"""

    def __init__(
        self,
        *,
        result: FavoriteEntity | None = None,
        error: Exception | None = None,
    ) -> None:
        """戻り値または例外を受け取って初期化する。"""

        self.received_video_id: str | None = None
        self._result = result
        self._error = error

    async def execute(self, video_id: str) -> FavoriteEntity:
        """受け取った動画 ID を記録し、指定された結果を返す。"""

        self.received_video_id = video_id
        if self._error is not None:
            raise self._error
        if self._result is None:
            raise AssertionError("result が未設定です。")
        return self._result


@pytest.fixture
def test_app() -> Iterator[FastAPI]:
    """router 単体テスト用の FastAPI app を返す。"""

    app = FastAPI()
    app.include_router(router)
    yield app
    app.dependency_overrides.clear()


class TestFavoritesRouter:
    """favorites_router の HTTP 入出力と例外変換を確認する。"""

    def test_list_favorites_returns_items_and_pagination_metadata(
        self,
        test_app: FastAPI,
    ) -> None:
        """一覧取得は items とページング情報を 200 で返す。"""

        # Arrange
        listed_item = _build_entity(
            video_id="videoid0001",
            title="ライブ映像",
            tags=["music", "live"],
        )
        usecase = ListFavoritesSpyUsecase(
            ListFavoritesResult(items=[listed_item], total=3)
        )
        test_app.dependency_overrides[get_list_favorites_usecase] = lambda: usecase
        client = TestClient(test_app)

        # Act
        response = client.get("/v1/favorites", params={"limit": 2, "offset": 1})

        # Assert
        assert response.status_code == 200
        assert usecase.called_with == (2, 1)
        payload = response.json()
        assert payload["total"] == 3
        assert payload["limit"] == 2
        assert payload["offset"] == 1
        assert payload["items"] == [
            {
                "videoId": "videoid0001",
                "title": "ライブ映像",
                "channelName": "チャンネル名",
                "thumbnailUrl": "https://example.com/thumb.jpg",
                "memo": "あとで見る",
                "tags": ["music", "live"],
                "createdAt": "2025-01-02T03:04:05Z",
                "updatedAt": "2025-01-03T04:05:06Z",
            }
        ]

    def test_list_favorites_accepts_x_request_id_header(
        self,
        test_app: FastAPI,
    ) -> None:
        """X-Request-Id ヘッダー付きでも一覧取得できる。"""

        # Arrange
        usecase = ListFavoritesSpyUsecase(ListFavoritesResult(items=[], total=0))
        test_app.dependency_overrides[get_list_favorites_usecase] = lambda: usecase
        client = TestClient(test_app)

        # Act
        response = client.get(
            "/v1/favorites",
            headers={"X-Request-Id": _REQUEST_ID},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "items": [],
            "total": 0,
            "limit": 20,
            "offset": 0,
        }
        assert usecase.called_with == (20, 0)

    def test_add_favorite_returns_created_and_passes_request_body_to_usecase(
        self,
        test_app: FastAPI,
    ) -> None:
        """追加成功時は 201 を返し request body を usecase へ渡す。"""

        # Arrange
        expected_input = AddFavoriteInput(
            video_id="videoid0002",
            title="あとで見る動画",
            channel_name="公式チャンネル",
            thumbnail_url="https://example.com/new-thumb.jpg",
            memo="メモ",
            tags=["watch-later", "favorite"],
        )
        usecase = AddFavoriteSpyUsecase(
            result=_build_entity(
                video_id=expected_input.video_id,
                title=expected_input.title,
                channel_name=expected_input.channel_name,
                thumbnail_url=expected_input.thumbnail_url,
                memo=expected_input.memo,
                tags=expected_input.tags,
            )
        )
        test_app.dependency_overrides[get_add_favorite_usecase] = lambda: usecase
        client = TestClient(test_app)
        request_body = {
            "videoId": "videoid0002",
            "title": "あとで見る動画",
            "channelName": "公式チャンネル",
            "thumbnailUrl": "https://example.com/new-thumb.jpg",
            "memo": "メモ",
            "tags": ["watch-later", "favorite"],
        }

        # Act
        response = client.post(
            "/v1/favorites",
            json=request_body,
            headers={"X-Request-Id": _REQUEST_ID},
        )

        # Assert
        assert response.status_code == 201
        assert usecase.received_input == expected_input
        assert response.json() == {
            "videoId": "videoid0002",
            "title": "あとで見る動画",
            "channelName": "公式チャンネル",
            "thumbnailUrl": "https://example.com/new-thumb.jpg",
            "memo": "メモ",
            "tags": ["watch-later", "favorite"],
            "createdAt": "2025-01-02T03:04:05Z",
            "updatedAt": "2025-01-03T04:05:06Z",
        }

    def test_add_favorite_returns_conflict_when_usecase_raises_already_exists_error(
        self,
        test_app: FastAPI,
    ) -> None:
        """重複追加時は AlreadyExistsError を 409 へ変換する。"""

        # Arrange
        usecase = AddFavoriteSpyUsecase(
            error=AlreadyExistsError("Favorite already exists")
        )
        test_app.dependency_overrides[get_add_favorite_usecase] = lambda: usecase
        client = TestClient(test_app)

        # Act
        response = client.post(
            "/v1/favorites",
            json={
                "videoId": "videoid0003",
                "title": "重複動画",
                "channelName": "公式チャンネル",
                "thumbnailUrl": "https://example.com/duplicate-thumb.jpg",
                "memo": "重複テスト",
                "tags": ["duplicate"],
            },
        )

        # Assert
        assert response.status_code == 409
        assert response.json() == {"detail": "Favorite already exists"}

    def test_get_favorite_returns_item(self, test_app: FastAPI) -> None:
        """単体取得成功時は 200 でお気に入り詳細を返す。"""

        # Arrange
        usecase = GetFavoriteSpyUsecase(
            result=_build_entity(
                video_id="videoid0004",
                title="視聴中の動画",
                tags=["now-playing"],
            )
        )
        test_app.dependency_overrides[get_get_favorite_usecase] = lambda: usecase
        client = TestClient(test_app)

        # Act
        response = client.get("/v1/favorites/videoid0004")

        # Assert
        assert response.status_code == 200
        assert usecase.received_video_id == "videoid0004"
        assert response.json() == {
            "videoId": "videoid0004",
            "title": "視聴中の動画",
            "channelName": "チャンネル名",
            "thumbnailUrl": "https://example.com/thumb.jpg",
            "memo": "あとで見る",
            "tags": ["now-playing"],
            "createdAt": "2025-01-02T03:04:05Z",
            "updatedAt": "2025-01-03T04:05:06Z",
        }

    def test_get_favorite_returns_not_found_when_usecase_raises_not_found_error(
        self,
        test_app: FastAPI,
    ) -> None:
        """未登録動画は NotFoundError を 404 へ変換する。"""

        # Arrange
        usecase = GetFavoriteSpyUsecase(
            error=NotFoundError("Favorite not found"),
        )
        test_app.dependency_overrides[get_get_favorite_usecase] = lambda: usecase
        client = TestClient(test_app)

        # Act
        response = client.get(
            "/v1/favorites/videoid0005",
            headers={"X-Request-Id": _REQUEST_ID},
        )

        # Assert
        assert response.status_code == 404
        assert usecase.received_video_id == "videoid0005"
        assert response.json() == {"detail": "Favorite not found"}

    def test_get_favorite_returns_422_when_video_id_is_invalid(
        self,
        test_app: FastAPI,
    ) -> None:
        """videoId が 11 文字パターンに一致しないと 422 を返す。"""

        # Arrange
        usecase = GetFavoriteSpyUsecase(result=_build_entity())
        test_app.dependency_overrides[get_get_favorite_usecase] = lambda: usecase
        client = TestClient(test_app)

        # Act
        response = client.get("/v1/favorites/invalid")

        # Assert
        assert response.status_code == 422
        assert usecase.received_video_id is None
        payload = response.json()
        assert payload["detail"][0]["type"] == "string_pattern_mismatch"
        assert payload["detail"][0]["loc"] == ["path", "videoId"]
