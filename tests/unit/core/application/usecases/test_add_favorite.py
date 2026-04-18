"""AddFavoriteUsecase の unit test。"""

from __future__ import annotations

import asyncio

import pytest

from core.application.exceptions import AlreadyExistsError
from core.application.ports.outbound.favorite_repository import FavoriteRepository
from core.application.usecases.add_favorite import (
    AddFavoriteInput,
    AddFavoriteUsecase,
)
from core.domain.favorite import FavoriteEntity


class SaveSpyRepository(FavoriteRepository):
    """save 呼び出しを観測する repository スパイ。"""

    def __init__(
        self,
        *,
        error: Exception | None = None,
    ) -> None:
        """戻り値または例外を制御できるように初期化する。"""

        self.saved_entity: FavoriteEntity | None = None
        self._error = error

    async def save(self, entity: FavoriteEntity) -> FavoriteEntity:
        """保存対象 entity を記録して返す。"""

        self.saved_entity = entity
        if self._error is not None:
            raise self._error
        return entity

    async def find_by_id(self, video_id: str) -> FavoriteEntity | None:
        """このテストでは利用しない。"""

        raise AssertionError("find_by_id はこのテストでは使いません。")

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


def _build_input(
    *,
    video_id: str = "videoid0001",
    title: str = "お気に入り動画",
    channel_name: str | None = "チャンネル名",
    thumbnail_url: str | None = "https://example.com/thumb.jpg",
    memo: str | None = "あとで見る",
    tags: list[str] | None = None,
) -> AddFavoriteInput:
    """テスト用の AddFavoriteInput を返す。"""

    return AddFavoriteInput(
        video_id=video_id,
        title=title,
        channel_name=channel_name,
        thumbnail_url=thumbnail_url,
        memo=memo,
        tags=tags,
    )


def test_execute_passes_entity_with_input_attributes_to_repo_save() -> None:
    """入力値から組み立てた entity を repository に渡す。"""

    # 準備
    repo = SaveSpyRepository()
    usecase = AddFavoriteUsecase(repo)
    input_data = _build_input(tags=["music", "live"])

    # 実行
    result = asyncio.run(usecase.execute(input_data))

    # 検証
    saved_entity = repo.saved_entity
    assert saved_entity is not None
    assert saved_entity.video_id == input_data.video_id
    assert saved_entity.title == input_data.title
    assert saved_entity.channel_name == input_data.channel_name
    assert saved_entity.thumbnail_url == input_data.thumbnail_url
    assert saved_entity.memo == input_data.memo
    assert saved_entity.tags == ["music", "live"]
    assert result == saved_entity


def test_execute_converts_none_tags_to_empty_list_before_save() -> None:
    """tags=None の入力は空配列へ正規化して保存する。"""

    # 準備
    repo = SaveSpyRepository()
    usecase = AddFavoriteUsecase(repo)
    input_data = _build_input(video_id="videoid0002", tags=None)

    # 実行
    asyncio.run(usecase.execute(input_data))

    # 検証
    saved_entity = repo.saved_entity
    assert saved_entity is not None
    assert saved_entity.tags == []


def test_execute_propagates_already_exists_error_from_repository() -> None:
    """repository が返した AlreadyExistsError をそのまま伝搬する。"""

    # 準備
    error = AlreadyExistsError("Favorite already exists")
    repo = SaveSpyRepository(error=error)
    usecase = AddFavoriteUsecase(repo)
    input_data = _build_input(video_id="videoid0003", tags=["music"])

    # 実行 / 検証
    with pytest.raises(AlreadyExistsError, match="Favorite already exists") as exc_info:
        asyncio.run(usecase.execute(input_data))

    assert exc_info.value.detail == "Favorite already exists"
