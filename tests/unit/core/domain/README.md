# core/domain テスト一覧

## test_favorite.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestFavoriteEntity | test_aware_datetimes_are_normalized_to_utc | FavoriteEntity | 正常系 | タイムゾーン付き日時を UTC に正規化すること |
| TestFavoriteEntity | test_default_tags_are_not_shared_between_instances | FavoriteEntity | 正常系 | tags のデフォルト値がインスタンス間で共有されないこと |
| TestFavoriteEntity | test_invalid_video_id_raises_value_error | FavoriteEntity | 境界値/異常系 | 不正な video_id を拒否すること |
| TestFavoriteEntity | test_empty_title_raises_value_error | FavoriteEntity | 境界値/異常系 | 空文字の title を拒否すること |
| TestFavoriteEntity | test_non_string_nullable_text_raises_type_error | FavoriteEntity | 異常系 | nullable text に文字列以外を与えると TypeError になること |
| TestFavoriteEntity | test_invalid_tags_raise_type_error | FavoriteEntity | 異常系 | tags に list[str] 以外を与えると TypeError になること |
| TestFavoriteEntity | test_naive_datetime_raises_value_error | FavoriteEntity | 境界値/異常系 | タイムゾーンなし日時を拒否すること |
