"""GetFavoriteUsecase の unit test。"""

from __future__ import annotations

import asyncio

import pytest

from core.application.exceptions import NotFoundError
from core.application.ports.outbound.favorite_repository import FavoriteRepository
from core.application.usecases.get_favorite import GetFavoriteUsecase
from core.domain.favorite import FavoriteEntity


class FindByIdStubRepository(FavoriteRepository):
    """find_by_id の戻り値を制御する repository スタブ。"""

    def __init__(self, entity: FavoriteEntity | None) -> None:
        """返却する entity を受け取って初期化する。"""

        self._entity = entity
        self.requested_video_id: str | None = None

    async def save(self, entity: FavoriteEntity) -> FavoriteEntity:
        """このテストでは利用しない。"""

        raise AssertionError("save はこのテストでは使いません。")

    async def find_by_id(self, video_id: str) -> FavoriteEntity | None:
        """指定された video_id を記録して事前設定した値を返す。"""

        self.requested_video_id = video_id
        return self._entity

    async def list_favorites(
        self,
        limit: int,
        offset: int,
    ) -> list[FavoriteEntity]:
        """このテストでは利用しない。"""

        raise AssertionError("list_favorites はこのテストでは使いません。")

    async def count(self) -> int:
        """このテストでは利用しない。"""

        raise AssertionError("count はこのテストでは使いません。")

    async def update(self, entity: FavoriteEntity) -> FavoriteEntity:
        """このテストでは利用しない。"""

        raise AssertionError("update はこのテストでは使いません。")

    async def delete(self, video_id: str) -> None:
        """このテストでは利用しない。"""

        raise AssertionError("delete はこのテストでは使いません。")


def _build_entity(video_id: str = "videoid0001") -> FavoriteEntity:
    """テスト用の FavoriteEntity を返す。"""

    return FavoriteEntity(
        video_id=video_id,
        title="お気に入り動画",
        channel_name="チャンネル名",
        thumbnail_url="https://example.com/thumb.jpg",
        memo="あとで見る",
        tags=["music"],
    )


def test_execute_returns_entity_when_repository_finds_favorite() -> None:
    """repository が entity を返したときはそのまま返す。"""

    # 準備
    entity = _build_entity()
    repo = FindByIdStubRepository(entity)
    usecase = GetFavoriteUsecase(repo)

    # 実行
    result = asyncio.run(usecase.execute(entity.video_id))

    # 検証
    assert repo.requested_video_id == entity.video_id
    assert result == entity


def test_execute_raises_not_found_error_when_repository_returns_none() -> None:
    """repository が None を返したときは NotFoundError を送出する。"""

    # 準備
    missing_video_id = "videoid9999"
    repo = FindByIdStubRepository(None)
    usecase = GetFavoriteUsecase(repo)

    # 実行 / 検証
    with pytest.raises(NotFoundError, match="Favorite not found") as exc_info:
        asyncio.run(usecase.execute(missing_video_id))

    assert exc_info.value.detail == "Favorite not found"
