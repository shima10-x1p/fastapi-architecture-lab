"""依存関係 provider の unit test。"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from core.adapters.outbound.csv_favorite_repository import CsvFavoriteRepository
from core.application.usecases.add_favorite import AddFavoriteUsecase
from core.application.usecases.get_favorite import GetFavoriteUsecase
from core.application.usecases.list_favorites import ListFavoritesUsecase
from core.shared.dependencies import (
    clear_csv_favorite_repository_cache,
    clear_settings_cache,
    get_add_favorite_usecase,
    get_csv_favorite_repository,
    get_get_favorite_usecase,
    get_list_favorites_usecase,
)
from core.shared.settings import AppSettings


@pytest.fixture(autouse=True)
def reset_dependency_caches() -> Iterator[None]:
    """各テストの前後で依存関係キャッシュを初期化する。"""

    clear_settings_cache()
    clear_csv_favorite_repository_cache()
    yield
    clear_settings_cache()
    clear_csv_favorite_repository_cache()


def test_get_csv_favorite_repository_reuses_repository_for_same_path(
    tmp_path: Path,
) -> None:
    """同じ CSV パスなら同じ repository を再利用する。"""

    # 準備
    csv_path = tmp_path / "favorites.csv"
    first_settings = AppSettings(favorites_csv_path=csv_path)
    second_settings = AppSettings(favorites_csv_path=csv_path)

    # 実行
    first_repo = get_csv_favorite_repository(first_settings)
    second_repo = get_csv_favorite_repository(second_settings)

    # 検証
    assert isinstance(first_repo, CsvFavoriteRepository)
    assert second_repo is first_repo


def test_get_csv_favorite_repository_recreates_repository_after_cache_clear(
    tmp_path: Path,
) -> None:
    """repository cache を破棄すると新しい instance を返す。"""

    # 準備
    settings = AppSettings(favorites_csv_path=tmp_path / "favorites.csv")
    first_repo = get_csv_favorite_repository(settings)

    # 実行
    clear_csv_favorite_repository_cache()
    second_repo = get_csv_favorite_repository(settings)

    # 検証
    assert second_repo is not first_repo


def test_get_add_favorite_usecase_returns_add_favorite_usecase(
    tmp_path: Path,
) -> None:
    """追加 usecase provider は AddFavoriteUsecase を返す。"""

    # 準備
    repo = CsvFavoriteRepository(tmp_path / "favorites.csv")

    # 実行
    usecase = get_add_favorite_usecase(repo)

    # 検証
    assert isinstance(usecase, AddFavoriteUsecase)


def test_get_get_favorite_usecase_returns_get_favorite_usecase(
    tmp_path: Path,
) -> None:
    """単体取得 usecase provider は GetFavoriteUsecase を返す。"""

    # 準備
    repo = CsvFavoriteRepository(tmp_path / "favorites.csv")

    # 実行
    usecase = get_get_favorite_usecase(repo)

    # 検証
    assert isinstance(usecase, GetFavoriteUsecase)


def test_get_list_favorites_usecase_returns_list_favorites_usecase(
    tmp_path: Path,
) -> None:
    """一覧取得 usecase provider は ListFavoritesUsecase を返す。"""

    # 準備
    repo = CsvFavoriteRepository(tmp_path / "favorites.csv")

    # 実行
    usecase = get_list_favorites_usecase(repo)

    # 検証
    assert isinstance(usecase, ListFavoritesUsecase)
