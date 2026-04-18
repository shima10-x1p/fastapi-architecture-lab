"""お気に入り動画を表す domain entity。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

_VIDEO_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


@dataclass(slots=True)
class FavoriteEntity:
    """
    お気に入り動画を表す domain entity。

    Attributes:
        video_id (str): YouTube の動画 ID。
        title (str): 動画タイトル。
        channel_name (str | None): チャンネル名。
        thumbnail_url (str | None): サムネイル URL。
        memo (str | None): 利用者メモ。
        tags (list[str]): 任意タグ一覧。
        created_at (datetime): 作成日時。
        updated_at (datetime): 更新日時。

    Exceptions:
        TypeError: 型が不正な値を受け取った場合に発生。
        ValueError: 動画 ID や日時などの不正値を受け取った場合に発生。
    """

    video_id: str
    title: str
    channel_name: str | None = None
    thumbnail_url: str | None = None
    memo: str | None = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """entity の不変条件を初期化時に検証する。"""

        self.video_id = _normalize_video_id(self.video_id)
        self.title = _normalize_title(self.title)
        self.channel_name = _normalize_nullable_text(
            self.channel_name,
            field_name="channel_name",
        )
        self.thumbnail_url = _normalize_nullable_text(
            self.thumbnail_url,
            field_name="thumbnail_url",
        )
        self.memo = _normalize_nullable_text(self.memo, field_name="memo")
        self.tags = _normalize_tags(self.tags)
        self.created_at = _normalize_datetime(
            self.created_at,
            field_name="created_at",
        )
        self.updated_at = _normalize_datetime(
            self.updated_at,
            field_name="updated_at",
        )


def _normalize_video_id(video_id: str) -> str:
    """
    YouTube の動画 ID を検証する。

    Args:
        video_id (str): 検証対象の動画 ID。

    Returns:
        str: 検証済みの動画 ID。

    Exceptions:
        TypeError: 文字列以外を受け取った場合に発生。
        ValueError: YouTube 動画 ID の形式に一致しない場合に発生。
    """
    if not isinstance(video_id, str):
        raise TypeError("video_id は文字列で指定してください。")

    if not _VIDEO_ID_PATTERN.fullmatch(video_id):
        raise ValueError("video_id は YouTube 動画 ID 形式で指定してください。")

    return video_id


def _normalize_title(title: str) -> str:
    """
    動画タイトルを検証する。

    Args:
        title (str): 検証対象のタイトル。

    Returns:
        str: 検証済みのタイトル。

    Exceptions:
        TypeError: 文字列以外を受け取った場合に発生。
        ValueError: 空文字列を受け取った場合に発生。
    """
    if not isinstance(title, str):
        raise TypeError("title は文字列で指定してください。")

    if title == "":
        raise ValueError("title は空文字列にできません。")

    return title


def _normalize_nullable_text(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    """
    nullable な文字列フィールドを検証する。

    Args:
        value (str | None): 検証対象の値。
        field_name (str): エラーメッセージ用のフィールド名。

    Returns:
        str | None: 検証済みの値。

    Exceptions:
        TypeError: 文字列または None 以外を受け取った場合に発生。
    """
    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(f"{field_name} は文字列または None で指定してください。")

    return value


def _normalize_tags(tags: list[str] | None) -> list[str]:
    """
    タグ一覧を検証する。

    Args:
        tags (list[str] | None): 検証対象のタグ一覧。

    Returns:
        list[str]: 検証済みのタグ一覧。

    Exceptions:
        TypeError: list[str] として扱えない値を受け取った場合に発生。
    """
    if tags is None:
        return []

    if not isinstance(tags, list):
        raise TypeError("tags は文字列の list で指定してください。")

    normalized_tags: list[str] = []
    for tag in tags:
        if not isinstance(tag, str):
            raise TypeError("tags の各要素は文字列で指定してください。")
        normalized_tags.append(tag)

    return normalized_tags


def _normalize_datetime(value: datetime, *, field_name: str) -> datetime:
    """
    datetime 値を検証し、UTC へ正規化する。

    Args:
        value (datetime): 検証対象の日時。
        field_name (str): エラーメッセージ用のフィールド名。

    Returns:
        datetime: UTC に正規化した日時。

    Exceptions:
        TypeError: datetime 以外を受け取った場合に発生。
        ValueError: タイムゾーン未設定の日時を受け取った場合に発生。
    """
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} は datetime で指定してください。")

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} にはタイムゾーン付き日時を指定してください。")

    return value.astimezone(UTC)
