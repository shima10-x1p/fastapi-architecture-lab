# core/adapters/outbound テスト一覧

## test_csv_favorite_repository.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestCsvFavoriteRepository | test_count_creates_parent_directory_and_header_on_first_use | CsvFavoriteRepository | 正常系 | 初回利用時に親ディレクトリと CSV ヘッダーを自動作成すること |
| TestCsvFavoriteRepository | test_save_then_find_count_and_list_return_paginated_entities | CsvFavoriteRepository | 正常系 | 保存した entity を取得し件数とページング結果を返すこと |
| TestCsvFavoriteRepository | test_list_with_zero_limit_returns_empty_list | CsvFavoriteRepository | 境界値 | limit=0 で空配列を返すこと |
| TestCsvFavoriteRepository | test_list_with_negative_limit_or_offset_raises_value_error | CsvFavoriteRepository | 異常系 | 負の limit または offset を拒否すること |
| TestCsvFavoriteRepository | test_save_with_duplicate_video_id_raises_already_exists_error | CsvFavoriteRepository | 異常系 | 重複 video_id の保存で AlreadyExistsError が発生すること |
| TestCsvFavoriteRepository | test_update_existing_entity_replaces_stored_row | CsvFavoriteRepository | 正常系 | 既存 entity の内容を更新後データで置き換えること |
| TestCsvFavoriteRepository | test_update_missing_entity_raises_not_found_error | CsvFavoriteRepository | 異常系 | 未登録 entity の更新で NotFoundError が発生すること |
| TestCsvFavoriteRepository | test_delete_existing_entity_removes_row | CsvFavoriteRepository | 正常系 | 既存 entity を削除すると再取得できなくなること |
| TestCsvFavoriteRepository | test_delete_missing_entity_raises_not_found_error | CsvFavoriteRepository | 異常系 | 未登録 entity の削除で NotFoundError が発生すること |
| TestCsvFavoriteRepository | test_nullable_text_fields_preserve_none_and_empty_string | CsvFavoriteRepository | 回帰 | nullable text が None と空文字を区別して往復できること |
| TestCsvFavoriteRepository | test_tags_and_timestamps_round_trip_through_csv_storage | CsvFavoriteRepository | 正常系/回帰 | tags の JSON と日時の ISO 8601 形式が保存後も復元できること |
