# core/application/usecases テスト一覧

## test_add_favorite.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_execute_passes_entity_with_input_attributes_to_repo_save | AddFavoriteUsecase | 正常系 | 入力値から組み立てた entity を repository.save に渡して返却値に反映すること |
| （なし） | test_execute_converts_none_tags_to_empty_list_before_save | AddFavoriteUsecase | 境界値 | tags=None を空配列へ正規化して保存すること |
| （なし） | test_execute_propagates_already_exists_error_from_repository | AddFavoriteUsecase / AlreadyExistsError | 異常系 | repository の重複例外をそのまま伝搬すること |

## test_get_favorite.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_execute_returns_entity_when_repository_finds_favorite | GetFavoriteUsecase | 正常系 | repository が返した entity をそのまま返すこと |
| （なし） | test_execute_raises_not_found_error_when_repository_returns_none | GetFavoriteUsecase / NotFoundError | 異常系 | 未登録の動画 ID では NotFoundError を送出すること |

## test_list_favorites.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_execute_passes_limit_and_offset_to_repository | ListFavoritesUsecase | 正常系 | limit と offset を repository.list_favorites へそのまま渡すこと |
| （なし） | test_execute_calls_repository_count_once | ListFavoritesUsecase | 正常系 | 一覧取得後に repository.count を 1 回呼び出すこと |
| （なし） | test_execute_returns_result_with_items_and_total | ListFavoritesUsecase / ListFavoritesResult | 正常系 | 取得した一覧と総件数を結果 DTO にまとめて返すこと |
