"""FastAPI で共有設定を注入するための依存関係定義。"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends

from core.adapters.outbound.csv_favorite_repository import CsvFavoriteRepository
from core.application.ports.outbound.favorite_repository import FavoriteRepository
from core.application.usecases.add_favorite import AddFavoriteUsecase
from core.application.usecases.get_favorite import GetFavoriteUsecase
from core.application.usecases.list_favorites import ListFavoritesUsecase
from core.shared.settings import AppSettings


@lru_cache
def get_settings() -> AppSettings:
    """環境変数から共有設定を読み込み、キャッシュして返す。"""

    return AppSettings()


def clear_settings_cache() -> None:
    """テストや再読み込み向けに設定キャッシュを破棄する。"""

    get_settings.cache_clear()


type SettingsDependency = Annotated[AppSettings, Depends(get_settings)]


def _normalize_csv_path(csv_path: Path) -> Path:
    """
    repository cache 用に CSV パス表現を正規化する。

    Args:
        csv_path (Path): 設定から受け取った CSV パス。

    Returns:
        Path: cache key として扱いやすい正規化済みパス。
    """

    return csv_path.expanduser().resolve()


@lru_cache
def _build_csv_favorite_repository(csv_path: Path) -> CsvFavoriteRepository:
    """
    CSV repository を path 単位で再利用しながら生成する。

    Args:
        csv_path (Path): 保存先 CSV ファイルパス。

    Returns:
        CsvFavoriteRepository: 再利用可能な repository。
    """

    return CsvFavoriteRepository(csv_path)


def clear_csv_favorite_repository_cache() -> None:
    """CSV repository の cache を破棄する。"""

    _build_csv_favorite_repository.cache_clear()


def get_csv_favorite_repository(
    settings: SettingsDependency,
) -> FavoriteRepository:
    """
    CSV 保存先を使う FavoriteRepository を返す。

    同じ CSV パスでは同じ repository を再利用し、repository 内部の
    `asyncio.Lock` がリクエストをまたいでも有効に働くようにする。

    Args:
        settings (SettingsDependency): アプリ共有設定。

    Returns:
        FavoriteRepository: CSV 保存先を使う repository 実装。
    """

    csv_path = _normalize_csv_path(settings.favorites_csv_path)
    return _build_csv_favorite_repository(csv_path)


type FavoriteRepositoryDependency = Annotated[
    FavoriteRepository,
    Depends(get_csv_favorite_repository),
]


def get_add_favorite_usecase(
    repo: FavoriteRepositoryDependency,
) -> AddFavoriteUsecase:
    """
    お気に入り追加 usecase を返す。

    Args:
        repo (FavoriteRepositoryDependency): お気に入り保存先。

    Returns:
        AddFavoriteUsecase: 追加 usecase。
    """

    return AddFavoriteUsecase(repo)


def get_get_favorite_usecase(
    repo: FavoriteRepositoryDependency,
) -> GetFavoriteUsecase:
    """
    お気に入り取得 usecase を返す。

    Args:
        repo (FavoriteRepositoryDependency): お気に入り保存先。

    Returns:
        GetFavoriteUsecase: 単体取得 usecase。
    """

    return GetFavoriteUsecase(repo)


def get_list_favorites_usecase(
    repo: FavoriteRepositoryDependency,
) -> ListFavoritesUsecase:
    """
    お気に入り一覧取得 usecase を返す。

    Args:
        repo (FavoriteRepositoryDependency): お気に入り保存先。

    Returns:
        ListFavoritesUsecase: 一覧取得 usecase。
    """

    return ListFavoritesUsecase(repo)
