"""お気に入り保存先の outbound port 定義。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.domain.favorite import FavoriteEntity


class FavoriteRepository(ABC):
    """
    お気に入り保存先の抽象インターフェース。

    Usecase はこの port だけに依存し、CSV や SQLite などの実装詳細を
    知らずに処理できる状態を維持する。
    """

    @abstractmethod
    async def save(self, entity: FavoriteEntity) -> FavoriteEntity:
        """
        新しいお気に入りを保存する。

        Args:
            entity (FavoriteEntity): 保存対象 entity。

        Returns:
            FavoriteEntity: 保存した entity。
        """

    @abstractmethod
    async def find_by_id(self, video_id: str) -> FavoriteEntity | None:
        """
        動画 ID でお気に入りを取得する。

        Args:
            video_id (str): 検索対象の動画 ID。

        Returns:
            FavoriteEntity | None: 見つかった entity。未登録なら None。
        """

    @abstractmethod
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
        """

    @abstractmethod
    async def count(self) -> int:
        """
        登録済みお気に入り件数を返す。

        Returns:
            int: 総件数。
        """

    @abstractmethod
    async def update(self, entity: FavoriteEntity) -> FavoriteEntity:
        """
        既存のお気に入りを更新する。

        Args:
            entity (FavoriteEntity): 更新後の entity。

        Returns:
            FavoriteEntity: 更新後 entity。
        """

    @abstractmethod
    async def delete(self, video_id: str) -> None:
        """
        動画 ID でお気に入りを削除する。

        Args:
            video_id (str): 削除対象の動画 ID。
        """
