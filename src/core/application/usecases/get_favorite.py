"""お気に入り単体取得 usecase。"""

from __future__ import annotations

from core.application.exceptions import NotFoundError
from core.application.ports.outbound.favorite_repository import FavoriteRepository
from core.domain.favorite import FavoriteEntity


class GetFavoriteUsecase:
    """動画 ID でお気に入りを 1 件取得する usecase。"""

    def __init__(self, repo: FavoriteRepository) -> None:
        """
        usecase が利用する repository を受け取る。

        Args:
            repo (FavoriteRepository): お気に入り保存先。
        """

        self._repo = repo

    async def execute(self, video_id: str) -> FavoriteEntity:
        """
        動画 ID でお気に入りを取得する。

        Args:
            video_id (str): 取得対象の動画 ID。

        Returns:
            FavoriteEntity: 見つかったお気に入り。

        Exceptions:
            NotFoundError: 対象の動画 ID が未登録の場合に発生。
        """

        entity = await self._repo.find_by_id(video_id)
        if entity is None:
            raise NotFoundError("Favorite not found")

        return entity
