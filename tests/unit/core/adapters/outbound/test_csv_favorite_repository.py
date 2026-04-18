"""CsvFavoriteRepository の unit test。"""

from __future__ import annotations

import asyncio
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.adapters.outbound.csv_favorite_repository import CsvFavoriteRepository
from core.application.exceptions import AlreadyExistsError, NotFoundError
from core.domain.favorite import FavoriteEntity


def _build_entity(
    index: int,
    *,
    title: str | None = None,
    channel_name: str | None = "channel",
    thumbnail_url: str | None = "https://example.com/thumb.jpg",
    memo: str | None = "memo",
    tags: list[str] | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> FavoriteEntity:
    """テスト用の FavoriteEntity を返す。"""
    jst = timezone(timedelta(hours=9))

    if title is None:
        title = f"title-{index}"
    if tags is None:
        tags = [f"tag-{index}"]
    if created_at is None:
        created_at = datetime(2025, 1, 1, 12, index, 0, tzinfo=jst)
    if updated_at is None:
        updated_at = datetime(2025, 1, 2, 12, index, 0, tzinfo=jst)

    return FavoriteEntity(
        video_id=f"video{index:06d}",
        title=title,
        channel_name=channel_name,
        thumbnail_url=thumbnail_url,
        memo=memo,
        tags=tags,
        created_at=created_at,
        updated_at=updated_at,
    )


def _read_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    """CSV の全行を読み込む。"""
    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


class TestCsvFavoriteRepository:
    """CsvFavoriteRepository の永続化挙動を確認する。"""

    def test_count_creates_parent_directory_and_header_on_first_use(
        self,
        tmp_path: Path,
    ) -> None:
        """初回利用時に親ディレクトリとヘッダーを自動作成する。"""
        # Arrange
        csv_path = tmp_path / "nested" / "favorites.csv"

        async def scenario() -> int:
            repo = CsvFavoriteRepository(csv_path)
            return await repo.count()

        # Act
        count = asyncio.run(scenario())

        # Assert
        assert count == 0
        assert csv_path.parent.exists()
        assert csv_path.exists()
        assert csv_path.read_text(encoding="utf-8").splitlines()[0] == (
            "video_id,title,channel_name,thumbnail_url,memo,tags,created_at,updated_at"
        )

    def test_save_then_find_count_and_list_return_paginated_entities(
        self,
        tmp_path: Path,
    ) -> None:
        """保存済み entity を取得し、件数とページング結果を返す。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        first = _build_entity(1)
        second = _build_entity(2)
        third = _build_entity(3)

        async def scenario() -> tuple[int, FavoriteEntity | None, list[FavoriteEntity]]:
            repo = CsvFavoriteRepository(csv_path)
            await repo.save(first)
            await repo.save(second)
            await repo.save(third)
            return (
                await repo.count(),
                await repo.find_by_id(second.video_id),
                await repo.list_favorites(limit=2, offset=1),
            )

        # Act
        count, found, paginated = asyncio.run(scenario())

        # Assert
        assert count == 3
        assert found == second
        assert paginated == [second, third]

    def test_list_with_zero_limit_returns_empty_list(self, tmp_path: Path) -> None:
        """limit=0 では空配列を返す。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        entity = _build_entity(1)

        async def scenario() -> list[FavoriteEntity]:
            repo = CsvFavoriteRepository(csv_path)
            await repo.save(entity)
            return await repo.list_favorites(limit=0, offset=0)

        # Act
        favorites = asyncio.run(scenario())

        # Assert
        assert favorites == []

    @pytest.mark.parametrize(
        ("limit", "offset", "message"),
        [(-1, 0, "limit"), (1, -1, "offset")],
    )
    def test_list_with_negative_limit_or_offset_raises_value_error(
        self,
        tmp_path: Path,
        limit: int,
        offset: int,
        message: str,
    ) -> None:
        """負のページング値を拒否する。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"

        async def scenario() -> None:
            repo = CsvFavoriteRepository(csv_path)
            with pytest.raises(ValueError, match=message):
                await repo.list_favorites(limit=limit, offset=offset)

        # Act / Assert
        asyncio.run(scenario())

    def test_save_with_duplicate_video_id_raises_already_exists_error(
        self,
        tmp_path: Path,
    ) -> None:
        """重複 video_id の保存を拒否する。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        original = _build_entity(1)
        duplicate = _build_entity(1, title="updated-title")

        async def scenario() -> AlreadyExistsError:
            repo = CsvFavoriteRepository(csv_path)
            await repo.save(original)
            with pytest.raises(
                AlreadyExistsError, match="Favorite already exists"
            ) as exc_info:
                await repo.save(duplicate)
            return exc_info.value

        # Act
        error = asyncio.run(scenario())

        # Assert
        assert error.detail == "Favorite already exists"

    def test_update_existing_entity_replaces_stored_row(self, tmp_path: Path) -> None:
        """既存 entity の更新内容を保存し直す。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        original = _build_entity(1)
        updated = _build_entity(
            1,
            title="updated-title",
            channel_name=None,
            thumbnail_url="",
            memo="updated memo",
            tags=["updated", "tag"],
        )

        async def scenario() -> FavoriteEntity | None:
            repo = CsvFavoriteRepository(csv_path)
            await repo.save(original)
            await repo.update(updated)
            return await repo.find_by_id(updated.video_id)

        # Act
        found = asyncio.run(scenario())

        # Assert
        assert found == updated

    def test_update_missing_entity_raises_not_found_error(
        self,
        tmp_path: Path,
    ) -> None:
        """未登録 entity の更新を拒否する。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        missing = _build_entity(1)

        async def scenario() -> NotFoundError:
            repo = CsvFavoriteRepository(csv_path)
            with pytest.raises(NotFoundError, match="Favorite not found") as exc_info:
                await repo.update(missing)
            return exc_info.value

        # Act
        error = asyncio.run(scenario())

        # Assert
        assert error.detail == "Favorite not found"

    def test_delete_existing_entity_removes_row(self, tmp_path: Path) -> None:
        """既存 entity を削除すると再取得できなくなる。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        first = _build_entity(1)
        second = _build_entity(2)

        async def scenario() -> tuple[
            int, FavoriteEntity | None, FavoriteEntity | None
        ]:
            repo = CsvFavoriteRepository(csv_path)
            await repo.save(first)
            await repo.save(second)
            await repo.delete(first.video_id)
            return (
                await repo.count(),
                await repo.find_by_id(first.video_id),
                await repo.find_by_id(second.video_id),
            )

        # Act
        count, deleted, remaining = asyncio.run(scenario())

        # Assert
        assert count == 1
        assert deleted is None
        assert remaining == second

    def test_delete_missing_entity_raises_not_found_error(
        self,
        tmp_path: Path,
    ) -> None:
        """未登録 entity の削除を拒否する。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"

        async def scenario() -> NotFoundError:
            repo = CsvFavoriteRepository(csv_path)
            with pytest.raises(NotFoundError, match="Favorite not found") as exc_info:
                await repo.delete("video000001")
            return exc_info.value

        # Act
        error = asyncio.run(scenario())

        # Assert
        assert error.detail == "Favorite not found"

    def test_nullable_text_fields_preserve_none_and_empty_string(
        self,
        tmp_path: Path,
    ) -> None:
        """nullable text は None と空文字を区別して往復できる。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        entity = _build_entity(
            1,
            channel_name=None,
            thumbnail_url="",
            memo=None,
        )

        async def scenario() -> FavoriteEntity | None:
            repo = CsvFavoriteRepository(csv_path)
            await repo.save(entity)
            return await repo.find_by_id(entity.video_id)

        # Act
        found = asyncio.run(scenario())

        # Assert
        assert found is not None
        assert found.channel_name is None
        assert found.thumbnail_url == ""
        assert found.memo is None

    def test_tags_and_timestamps_round_trip_through_csv_storage(
        self,
        tmp_path: Path,
    ) -> None:
        """tags と日時を CSV 保存形式のまま往復できる。"""
        # Arrange
        csv_path = tmp_path / "favorites.csv"
        entity = _build_entity(
            1,
            tags=["音楽", "live"],
            created_at=datetime(
                2025, 2, 3, 4, 5, 6, tzinfo=timezone(timedelta(hours=9))
            ),
            updated_at=datetime(
                2025, 2, 4, 7, 8, 9, tzinfo=timezone(timedelta(hours=-5))
            ),
        )

        async def scenario() -> FavoriteEntity | None:
            repo = CsvFavoriteRepository(csv_path)
            await repo.save(entity)
            return await repo.find_by_id(entity.video_id)

        # Act
        found = asyncio.run(scenario())
        row = _read_csv_rows(csv_path)[0]

        # Assert
        assert row["tags"] == json.dumps(entity.tags, ensure_ascii=False)
        assert row["created_at"] == entity.created_at.isoformat()
        assert row["updated_at"] == entity.updated_at.isoformat()
        assert found == entity
