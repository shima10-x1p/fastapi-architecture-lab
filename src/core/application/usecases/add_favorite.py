"""お気に入り追加 usecase。"""

from __future__ import annotations

from dataclasses import dataclass

from core.application.ports.outbound.favorite_repository import FavoriteRepository
from core.domain.favorite import FavoriteEntity


@dataclass(slots=True)
class AddFavoriteInput:
    """
    お気に入り追加 usecase の入力値。

    Attributes:
        video_id (str): YouTube の動画 ID。
        title (str): 動画タイトル。
        channel_name (str | None): チャンネル名。
        thumbnail_url (str | None): サムネイル URL。
        memo (str | None): 利用者メモ。
        tags (list[str] | None): 任意タグ一覧。
    """

    video_id: str
    title: str
    channel_name: str | None = None
    thumbnail_url: str | None = None
    memo: str | None = None
    tags: list[str] | None = None


class AddFavoriteUsecase:
    """
    新しいお気に入りを追加する usecase。

    repository への保存前に domain entity を組み立て、入力値検証は
    `FavoriteEntity` の不変条件へ委譲する。
    """

    def __init__(self, repo: FavoriteRepository) -> None:
        """
        usecase が利用する repository を受け取る。

        Args:
            repo (FavoriteRepository): お気に入り保存先。
        """

        self._repo = repo

    async def execute(self, input_data: AddFavoriteInput) -> FavoriteEntity:
        """
        新しいお気に入りを追加する。

        Args:
            input_data (AddFavoriteInput): 追加対象の入力値。

        Returns:
            FavoriteEntity: 保存されたお気に入り。
        """

        entity = FavoriteEntity(
            video_id=input_data.video_id,
            title=input_data.title,
            channel_name=input_data.channel_name,
            thumbnail_url=input_data.thumbnail_url,
            memo=input_data.memo,
            tags=[] if input_data.tags is None else input_data.tags,
        )
        return await self._repo.save(entity)
