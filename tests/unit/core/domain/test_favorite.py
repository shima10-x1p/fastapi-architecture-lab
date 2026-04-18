"""FavoriteEntity の unit test。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest

from core.domain.favorite import FavoriteEntity


def _build_favorite_kwargs() -> dict[str, object]:
    """有効な FavoriteEntity 引数を返す。"""
    return {
        "video_id": "abc123_DEF-",
        "title": "お気に入り動画",
        "channel_name": "channel",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "memo": "memo",
        "tags": ["tag1", "tag2"],
        "created_at": datetime(
            2025, 1, 2, 12, 34, 56, tzinfo=timezone(timedelta(hours=9))
        ),
        "updated_at": datetime(
            2025, 1, 3, 1, 2, 3, tzinfo=timezone(timedelta(hours=-5))
        ),
    }


class TestFavoriteEntity:
    """FavoriteEntity の検証をまとめる。"""

    def test_aware_datetimes_are_normalized_to_utc(self) -> None:
        """タイムゾーン付き日時を UTC に正規化する。"""
        # Arrange
        kwargs = _build_favorite_kwargs()

        # Act
        entity = FavoriteEntity(**kwargs)

        # Assert
        assert entity.created_at == datetime(2025, 1, 2, 3, 34, 56, tzinfo=UTC)
        assert entity.updated_at == datetime(2025, 1, 3, 6, 2, 3, tzinfo=UTC)
        assert entity.channel_name == "channel"
        assert entity.thumbnail_url == "https://example.com/thumb.jpg"
        assert entity.memo == "memo"

    def test_default_tags_are_not_shared_between_instances(self) -> None:
        """tags のデフォルト値がインスタンス間で共有されない。"""
        # Arrange
        first = FavoriteEntity(video_id="video000001", title="first")
        second = FavoriteEntity(video_id="video000002", title="second")

        # Act
        first.tags.append("shared?")

        # Assert
        assert first.tags == ["shared?"]
        assert second.tags == []

    @pytest.mark.parametrize(
        "video_id",
        ["short", "video0000012", "invalid!*id"],
    )
    def test_invalid_video_id_raises_value_error(self, video_id: str) -> None:
        """不正な video_id を拒否する。"""
        # Arrange
        kwargs = _build_favorite_kwargs()
        kwargs["video_id"] = video_id

        # Act / Assert
        with pytest.raises(ValueError, match="video_id"):
            FavoriteEntity(**kwargs)

    def test_empty_title_raises_value_error(self) -> None:
        """空文字タイトルを拒否する。"""
        # Arrange
        kwargs = _build_favorite_kwargs()
        kwargs["title"] = ""

        # Act / Assert
        with pytest.raises(ValueError, match="title"):
            FavoriteEntity(**kwargs)

    @pytest.mark.parametrize("field_name", ["channel_name", "thumbnail_url", "memo"])
    def test_non_string_nullable_text_raises_type_error(
        self,
        field_name: str,
    ) -> None:
        """nullable text には str または None だけを許可する。"""
        # Arrange
        kwargs = _build_favorite_kwargs()
        kwargs[field_name] = 123

        # Act / Assert
        with pytest.raises(TypeError, match=field_name):
            FavoriteEntity(**kwargs)

    @pytest.mark.parametrize(
        ("tags", "message"),
        [
            ("not-a-list", "tags は文字列の list"),
            (["ok", 1], "tags の各要素は文字列"),
        ],
    )
    def test_invalid_tags_raise_type_error(
        self,
        tags: object,
        message: str,
    ) -> None:
        """tags は list[str] だけを許可する。"""
        # Arrange
        kwargs = _build_favorite_kwargs()
        kwargs["tags"] = tags

        # Act / Assert
        with pytest.raises(TypeError, match=message):
            FavoriteEntity(**kwargs)

    @pytest.mark.parametrize("field_name", ["created_at", "updated_at"])
    def test_naive_datetime_raises_value_error(self, field_name: str) -> None:
        """タイムゾーンなし日時を拒否する。"""
        # Arrange
        kwargs = _build_favorite_kwargs()
        kwargs[field_name] = datetime(2025, 1, 2, 12, 34, 56)

        # Act / Assert
        with pytest.raises(ValueError, match="タイムゾーン付き日時"):
            FavoriteEntity(**kwargs)
