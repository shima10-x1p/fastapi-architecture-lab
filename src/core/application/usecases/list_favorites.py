"""お気に入り一覧取得 usecase。"""

from __future__ import annotations

from dataclasses import dataclass

from core.application.ports.outbound.favorite_repository import FavoriteRepository
from core.domain.favorite import FavoriteEntity


@dataclass(frozen=True, slots=True)
class ListFavoritesResult:
    """
    お気に入り一覧取得結果。

    Attributes:
        items (list[FavoriteEntity]): 現在ページに含まれるお気に入り一覧。
        total (int): 登録済みお気に入り総件数。
    """

    items: list[FavoriteEntity]
    total: int


class ListFavoritesUsecase:
    """ページング条件付きでお気に入り一覧を返す usecase。"""

    def __init__(self, repo: FavoriteRepository) -> None:
        """
        usecase が利用する repository を受け取る。

        Args:
            repo (FavoriteRepository): お気に入り保存先。
        """

        self._repo = repo

    async def execute(self, limit: int, offset: int) -> ListFavoritesResult:
        """
        ページング条件付きでお気に入り一覧を取得する。

        Args:
            limit (int): 最大取得件数。
            offset (int): 取得開始位置。

        Returns:
            ListFavoritesResult: 一覧と総件数をまとめた結果。
        """

        items = await self._repo.list_favorites(limit=limit, offset=offset)
        total = await self._repo.count()
        return ListFavoritesResult(items=items, total=total)
