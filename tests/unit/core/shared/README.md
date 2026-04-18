# core/shared テスト一覧

## test_dependencies.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_get_csv_favorite_repository_reuses_repository_for_same_path | get_csv_favorite_repository | 正常系 | 同じ CSV パスでは同じ repository instance を再利用すること |
| （なし） | test_get_csv_favorite_repository_recreates_repository_after_cache_clear | get_csv_favorite_repository / clear_csv_favorite_repository_cache | 回帰 | cache 破棄後は新しい repository instance を返すこと |
| （なし） | test_get_add_favorite_usecase_returns_add_favorite_usecase | get_add_favorite_usecase | 正常系 | 追加 usecase provider が AddFavoriteUsecase を返すこと |
| （なし） | test_get_get_favorite_usecase_returns_get_favorite_usecase | get_get_favorite_usecase | 正常系 | 単体取得 usecase provider が GetFavoriteUsecase を返すこと |
| （なし） | test_get_list_favorites_usecase_returns_list_favorites_usecase | get_list_favorites_usecase | 正常系 | 一覧取得 usecase provider が ListFavoritesUsecase を返すこと |

## test_exceptions.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_domain_error_stores_message_and_returns_it_from_str | DomainError | 正常系 | message 属性と文字列表現に同じメッセージを保持すること |
| （なし） | test_application_error_stores_message_without_resource_id | ApplicationError | 正常系 | resource_id 未指定時に message と None を保持すること |
| （なし） | test_application_error_stores_message_and_resource_id | ApplicationError | 正常系 | resource_id 指定時に message と resource_id を保持すること |
| （なし） | test_not_found_error_uses_default_message_when_message_is_omitted | NotFoundError | 正常系 | message 未指定時に resource_id を含む既定メッセージを使うこと |
| （なし） | test_conflict_error_uses_default_message_when_message_is_omitted | ConflictError | 正常系 | message 未指定時に resource_id を含む既定メッセージを使うこと |
| （なし） | test_not_found_error_accepts_message_override | NotFoundError | 正常系 | 明示したメッセージを既定値より優先すること |
| （なし） | test_conflict_error_accepts_message_override | ConflictError | 正常系 | 明示したメッセージを既定値より優先すること |
| （なし） | test_application_error_raises_value_error_for_blank_resource_id | ApplicationError | 境界値/異常系 | 空文字列と空白のみの resource_id を拒否すること |
| （なし） | test_not_found_error_raises_value_error_for_blank_resource_id | NotFoundError | 境界値/異常系 | 空文字列と空白のみの resource_id を拒否すること |
| （なし） | test_conflict_error_raises_value_error_for_blank_resource_id | ConflictError | 境界値/異常系 | 空文字列と空白のみの resource_id を拒否すること |
| （なし） | test_not_found_error_and_conflict_error_are_application_error_instances | NotFoundError / ConflictError | 正常系 | どちらも ApplicationError の派生例外であること |
| （なし） | test_domain_error_is_not_an_application_error | DomainError | 正常系 | DomainError が ApplicationError とは別系統であること |
| （なし） | test_core_shared_re_exports_exception_classes | core.shared | 回帰 | パッケージ公開 API から共有例外クラスを参照できること |

## test_logger.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_configure_logging_uses_default_settings_when_env_vars_are_missing | configure_logging | 正常系 | 環境変数未設定時に既定のログレベルとフォーマットで初期化されること |
| （なし） | test_configure_logging_applies_env_var_settings | configure_logging | 正常系 | 環境変数で指定したログレベルとフォーマットが反映されること |
| （なし） | test_configure_logging_does_not_duplicate_stdout_handler | configure_logging | 回帰 | 初期化を繰り返しても標準出力ハンドラーが重複しないこと |
| （なし） | test_configure_logging_rejects_invalid_log_level | configure_logging | 異常系 | 不正なログレベル文字列を拒否すること |
| （なし） | test_get_logger_returns_named_logger | get_logger | 正常系 | 指定名の logger を取得できること |

## test_settings.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_app_settings_uses_defaults_when_environment_variables_are_missing | AppSettings | 正常系 | 環境変数未設定時に既定値を採用すること |
| （なし） | test_get_settings_reads_values_from_os_environment | get_settings | 正常系 | OS 環境変数から設定値を読み込めること |
| （なし） | test_app_settings_uses_default_favorites_csv_path | AppSettings | 正常系 | favorites_csv_path の既定値が data/favorites.csv であること |
| （なし） | test_app_settings_reads_favorites_csv_path_from_environment | AppSettings | 正常系 | FAVORITES_CSV_PATH で CSV パスを上書きできること |
| （なし） | test_app_settings_rejects_empty_app_name | AppSettings | 境界値/異常系 | 空文字のアプリ名を不正値として扱うこと |
| （なし） | test_get_settings_cache_can_be_cleared_for_reloading | get_settings / clear_settings_cache | 回帰 | 設定キャッシュ破棄後に最新の環境変数を再読込できること |
