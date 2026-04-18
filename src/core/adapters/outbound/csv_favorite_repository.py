"""CSV を保存先に使う FavoriteRepository 実装。"""

from __future__ import annotations

import asyncio
import csv
import json
from datetime import datetime
from pathlib import Path

from core.application.exceptions import AlreadyExistsError, NotFoundError
from core.application.ports.outbound.favorite_repository import (
    FavoriteRepository,
)
from core.domain.favorite import FavoriteEntity

_CSV_HEADERS = (
    "video_id",
    "title",
    "channel_name",
    "thumbnail_url",
    "memo",
    "tags",
    "created_at",
    "updated_at",
)


class CsvFavoriteRepository(FavoriteRepository):
    """
    CSV ファイルへお気に入りを永続化する repository。

    まず小さく差し替え可能な保存先を用意するため、全件読込 / 全件書込の
    シンプルな実装を採用する。将来 SQLite や S3 実装へ差し替える際も、
    呼び出し側は port 契約を変えずに利用できる。
    """

    def __init__(self, csv_path: Path) -> None:
        """
        repository の保存先を初期化する。

        Args:
            csv_path (Path): 保存先 CSV ファイルの絶対または相対パス。
        """
        self._csv_path = csv_path
        self._lock = asyncio.Lock()

    async def save(self, entity: FavoriteEntity) -> FavoriteEntity:
        """
        新しいお気に入りを保存する。

        Args:
            entity (FavoriteEntity): 保存対象 entity。

        Returns:
            FavoriteEntity: 保存した entity。

        Exceptions:
            AlreadyExistsError: 同じ動画 ID が既に存在する場合に発生。
        """
        async with self._lock:
            rows = await asyncio.to_thread(self._read_rows)
            if _find_row_index(rows, entity.video_id) is not None:
                raise AlreadyExistsError("Favorite already exists")

            rows.append(_serialize_entity(entity))
            await asyncio.to_thread(self._write_rows, rows)

        return entity

    async def find_by_id(self, video_id: str) -> FavoriteEntity | None:
        """
        動画 ID でお気に入りを取得する。

        Args:
            video_id (str): 検索対象の動画 ID。

        Returns:
            FavoriteEntity | None: 見つかった entity。未登録なら None。
        """
        async with self._lock:
            rows = await asyncio.to_thread(self._read_rows)

        row_index = _find_row_index(rows, video_id)
        if row_index is None:
            return None

        return _deserialize_row(rows[row_index])

    async def list_favorites(
        self,
        limit: int,
        offset: int,
    ) -> list[FavoriteEntity]:
        """
        ページング条件付きでお気に入り一覧を取得する。

        Args:
            limit (int): 最大取得件数。
            offset (int): 取得開始位置。

        Returns:
            list[FavoriteEntity]: 条件に一致した entity 一覧。

        Exceptions:
            ValueError: limit または offset が不正な場合に発生。
        """
        if limit < 0:
            raise ValueError("limit は 0 以上で指定してください。")
        if offset < 0:
            raise ValueError("offset は 0 以上で指定してください。")

        async with self._lock:
            rows = await asyncio.to_thread(self._read_rows)

        paginated_rows = rows[offset : offset + limit]
        return [_deserialize_row(row) for row in paginated_rows]

    async def count(self) -> int:
        """
        登録済みお気に入り件数を返す。

        Returns:
            int: 総件数。
        """
        async with self._lock:
            rows = await asyncio.to_thread(self._read_rows)

        return len(rows)

    async def update(self, entity: FavoriteEntity) -> FavoriteEntity:
        """
        既存のお気に入りを更新する。

        Args:
            entity (FavoriteEntity): 更新後 entity。

        Returns:
            FavoriteEntity: 更新後 entity。

        Exceptions:
            NotFoundError: 更新対象が存在しない場合に発生。
        """
        async with self._lock:
            rows = await asyncio.to_thread(self._read_rows)
            row_index = _find_row_index(rows, entity.video_id)
            if row_index is None:
                raise NotFoundError("Favorite not found")

            rows[row_index] = _serialize_entity(entity)
            await asyncio.to_thread(self._write_rows, rows)

        return entity

    async def delete(self, video_id: str) -> None:
        """
        動画 ID でお気に入りを削除する。

        Args:
            video_id (str): 削除対象の動画 ID。

        Exceptions:
            NotFoundError: 削除対象が存在しない場合に発生。
        """
        async with self._lock:
            rows = await asyncio.to_thread(self._read_rows)
            row_index = _find_row_index(rows, video_id)
            if row_index is None:
                raise NotFoundError("Favorite not found")

            rows.pop(row_index)
            await asyncio.to_thread(self._write_rows, rows)

    def _read_rows(self) -> list[dict[str, str]]:
        """
        CSV を読み込み、行一覧として返す。

        Returns:
            list[dict[str, str]]: CSV の全行。
        """
        self._ensure_storage_ready()

        with self._csv_path.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            return [
                {header: row.get(header, "") for header in _CSV_HEADERS}
                for row in reader
            ]

    def _write_rows(self, rows: list[dict[str, str]]) -> None:
        """
        行一覧を CSV へ書き戻す。

        Args:
            rows (list[dict[str, str]]): 書込対象の全行。
        """
        self._ensure_storage_ready()

        with self._csv_path.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(_CSV_HEADERS))
            writer.writeheader()
            writer.writerows(rows)

    def _ensure_storage_ready(self) -> None:
        """
        親ディレクトリと CSV ヘッダーを初期化する。

        CSV adapter 単体で完結させることで、DI 設定側に初期化責務を漏らさ
        ずに済むようにしている。
        """
        self._csv_path.parent.mkdir(parents=True, exist_ok=True)
        if self._csv_path.exists() and self._csv_path.stat().st_size > 0:
            return

        with self._csv_path.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(_CSV_HEADERS))
            writer.writeheader()


def _find_row_index(rows: list[dict[str, str]], video_id: str) -> int | None:
    """
    動画 ID に対応する行番号を返す。

    Args:
        rows (list[dict[str, str]]): 探索対象の CSV 行一覧。
        video_id (str): 対象の動画 ID。

    Returns:
        int | None: 見つかった行番号。未登録なら None。
    """
    for index, row in enumerate(rows):
        if row["video_id"] == video_id:
            return index

    return None


def _serialize_entity(entity: FavoriteEntity) -> dict[str, str]:
    """
    entity を CSV 保存用の 1 行へ変換する。

    Args:
        entity (FavoriteEntity): 変換対象 entity。

    Returns:
        dict[str, str]: CSV へ保存可能な 1 行。
    """
    return {
        "video_id": entity.video_id,
        "title": entity.title,
        "channel_name": _serialize_nullable_text(entity.channel_name),
        "thumbnail_url": _serialize_nullable_text(entity.thumbnail_url),
        "memo": _serialize_nullable_text(entity.memo),
        "tags": json.dumps(entity.tags, ensure_ascii=False),
        "created_at": entity.created_at.isoformat(),
        "updated_at": entity.updated_at.isoformat(),
    }


def _deserialize_row(row: dict[str, str]) -> FavoriteEntity:
    """
    CSV の 1 行を entity へ戻す。

    Args:
        row (dict[str, str]): 読込済み CSV 行。

    Returns:
        FavoriteEntity: 復元した entity。
    """
    return FavoriteEntity(
        video_id=row["video_id"],
        title=row["title"],
        channel_name=_deserialize_nullable_text(
            row["channel_name"],
            field_name="channel_name",
        ),
        thumbnail_url=_deserialize_nullable_text(
            row["thumbnail_url"],
            field_name="thumbnail_url",
        ),
        memo=_deserialize_nullable_text(row["memo"], field_name="memo"),
        tags=_deserialize_tags(row["tags"]),
        created_at=_deserialize_datetime(
            row["created_at"],
            field_name="created_at",
        ),
        updated_at=_deserialize_datetime(
            row["updated_at"],
            field_name="updated_at",
        ),
    )


def _serialize_nullable_text(value: str | None) -> str:
    """
    null と空文字の差を保ったまま文字列を保存形式へ変換する。

    Args:
        value (str | None): 変換対象の文字列。

    Returns:
        str: JSON 文字列化した保存値。
    """
    return json.dumps(value, ensure_ascii=False)


def _deserialize_nullable_text(value: str, *, field_name: str) -> str | None:
    """
    保存形式の文字列を nullable text へ戻す。

    Args:
        value (str): CSV に保存された値。
        field_name (str): エラーメッセージ用のフィールド名。

    Returns:
        str | None: 復元した値。

    Exceptions:
        ValueError: 保存値が想定形式でない場合に発生。
    """
    decoded = json.loads(value)
    if decoded is None or isinstance(decoded, str):
        return decoded

    raise ValueError(f"{field_name} の保存値が不正です。")


def _deserialize_tags(value: str) -> list[str]:
    """
    保存形式の tags を list[str] へ戻す。

    Args:
        value (str): CSV に保存された tags 値。

    Returns:
        list[str]: 復元した tags。

    Exceptions:
        ValueError: 保存値が list[str] として不正な場合に発生。
    """
    decoded = json.loads(value)
    if not isinstance(decoded, list):
        raise ValueError("tags の保存値が不正です。")

    normalized_tags: list[str] = []
    for tag in decoded:
        if not isinstance(tag, str):
            raise ValueError("tags の保存値が不正です。")
        normalized_tags.append(tag)

    return normalized_tags


def _deserialize_datetime(value: str, *, field_name: str) -> datetime:
    """
    ISO 8601 文字列を datetime へ戻す。

    Args:
        value (str): CSV に保存された日時文字列。
        field_name (str): エラーメッセージ用のフィールド名。

    Returns:
        datetime: 復元した datetime。

    Exceptions:
        ValueError: ISO 8601 として解釈できない場合に発生。
    """
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} の保存値が不正です。") from exc
