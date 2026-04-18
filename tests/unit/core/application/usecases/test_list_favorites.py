"""ListFavoritesUsecase の unit test。"""

from __future__ import annotations

import asyncio

from core.application.ports.outbound.favorite_repository import FavoriteRepository
from core.application.usecases.list_favorites import (
    ListFavoritesResult,
    ListFavoritesUsecase,
)
from core.domain.favorite import FavoriteEntity


class ListFavoritesSpyRepository(FavoriteRepository):
    """一覧取得 usecase の呼び出しを観測する repository スパイ。"""

    def __init__(self, *, items: list[FavoriteEntity], total: int) -> None:
        """返却する一覧と総件数を受け取って初期化する。"""

        self._items = items
        self._total = total
        self.received_limit: int | None = None
        self.received_offset: int | None = None
        self.count_calls = 0

    async def save(self, entity: FavoriteEntity) -> FavoriteEntity:
        """このテストでは利用しない。"""

        raise AssertionError("save はこのテストでは使いません。")

    async def find_by_id(self, video_id: str) -> FavoriteEntity | None:
        """このテストでは利用しない。"""

        raise AssertionError("find_by_id はこのテストでは使いません。")

    async def list_favorites(
        self,
        limit: int,
        offset: int,
    ) -> list[FavoriteEntity]:
        """呼び出し時のページング条件を記録して一覧を返す。"""

        self.received_limit = limit
        self.received_offset = offset
        return self._items

    async def count(self) -> int:
        """呼び出し回数を記録して総件数を返す。"""

        self.count_calls += 1
        return self._total

    async def update(self, entity: FavoriteEntity) -> FavoriteEntity:
        """このテストでは利用しない。"""

        raise AssertionError("update はこのテストでは使いません。")

    async def delete(self, video_id: str) -> None:
        """このテストでは利用しない。"""

        raise AssertionError("delete はこのテストでは使いません。")


def _build_entity(index: int) -> FavoriteEntity:
    """テスト用の FavoriteEntity を返す。"""

    return FavoriteEntity(
        video_id=f"videoid{index:04d}",
        title=f"お気に入り動画 {index}",
        channel_name=f"channel-{index}",
        thumbnail_url=f"https://example.com/thumb-{index}.jpg",
        memo=f"memo-{index}",
        tags=[f"tag-{index}"],
    )


def test_execute_passes_limit_and_offset_to_repository() -> None:
    """limit と offset を repository.list_favorites へ伝搬する。"""

    # 準備
    repo = ListFavoritesSpyRepository(items=[], total=0)
    usecase = ListFavoritesUsecase(repo)

    # 実行
    asyncio.run(usecase.execute(limit=5, offset=10))

    # 検証
    assert repo.received_limit == 5
    assert repo.received_offset == 10


def test_execute_calls_repository_count_once() -> None:
    """一覧取得後に repository.count を 1 回呼び出す。"""

    # 準備
    repo = ListFavoritesSpyRepository(items=[_build_entity(1)], total=1)
    usecase = ListFavoritesUsecase(repo)

    # 実行
    asyncio.run(usecase.execute(limit=1, offset=0))

    # 検証
    assert repo.count_calls == 1


def test_execute_returns_result_with_items_and_total() -> None:
    """取得した一覧と総件数を ListFavoritesResult にまとめて返す。"""

    # 準備
    items = [_build_entity(1), _build_entity(2)]
    repo = ListFavoritesSpyRepository(items=items, total=7)
    usecase = ListFavoritesUsecase(repo)

    # 実行
    result = asyncio.run(usecase.execute(limit=2, offset=0))

    # 検証
    assert isinstance(result, ListFavoritesResult)
    assert result.items == items
    assert result.total == 7
