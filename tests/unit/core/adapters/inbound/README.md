# core/adapters/inbound テスト一覧

## test_favorites_router.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestFavoritesRouter | test_list_favorites_returns_items_and_pagination_metadata | favorites_router.list_favorites | 正常系 | 一覧取得が items・total・limit・offset を 200 で返すこと |
| TestFavoritesRouter | test_list_favorites_accepts_x_request_id_header | favorites_router.list_favorites | 正常系 | `X-Request-Id` ヘッダー付きでも一覧取得が正常動作すること |
| TestFavoritesRouter | test_add_favorite_returns_created_and_passes_request_body_to_usecase | favorites_router.add_favorite | 正常系 | POST body を AddFavoriteInput 相当へ変換して usecase に渡し 201 を返すこと |
| TestFavoritesRouter | test_add_favorite_returns_conflict_when_usecase_raises_already_exists_error | favorites_router.add_favorite / AlreadyExistsError | 異常系 | application の重複例外を 409 と detail に変換すること |
| TestFavoritesRouter | test_get_favorite_returns_item | favorites_router.get_favorite | 正常系 | 単体取得が 200 でお気に入り詳細を返すこと |
| TestFavoritesRouter | test_get_favorite_returns_not_found_when_usecase_raises_not_found_error | favorites_router.get_favorite / NotFoundError | 異常系 | application の未検出例外を 404 と detail に変換すること |
| TestFavoritesRouter | test_get_favorite_returns_422_when_video_id_is_invalid | favorites_router.get_favorite | 境界値/異常系 | 11 文字パターンに一致しない videoId を 422 で拒否すること |
