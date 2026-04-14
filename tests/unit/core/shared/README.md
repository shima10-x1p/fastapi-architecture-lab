# core/shared テスト一覧

## test_logging.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestGetLogger | test_returns_logger_instance | get_logger | 正常系 | Logger インスタンスを返すこと |
| TestGetLogger | test_logger_name_matches_argument | get_logger | 正常系 | 引数で指定した名前が Logger に設定されること |
| TestGetLogger | test_dunder_name_pattern | get_logger | 正常系 | `__name__` パターンで正しい名前の Logger を返すこと |
| TestConfigureLogging | test_sets_root_level_info | configure_logging | 正常系 | INFO レベルが root logger に設定されること |
| TestConfigureLogging | test_sets_root_level_debug | configure_logging | 正常系 | DEBUG レベルが root logger に設定されること |
| TestConfigureLogging | test_sets_root_level_warning | configure_logging | 正常系 | WARNING レベルが root logger に設定されること |
| TestConfigureLogging | test_unknown_level_falls_back_to_info | configure_logging | 異常系 | 不正なレベル文字列で INFO にフォールバックすること |
| TestConfigureLogging | test_adds_stream_handler | configure_logging | 正常系 | StreamHandler が追加されること |
| TestConfigureLogging | test_applies_custom_log_format | configure_logging | 正常系 | カスタムフォーマットが適用されること |
| TestConfigureLogging | test_repeated_calls_do_not_duplicate_handlers | configure_logging | 正常系 | 複数回呼び出してもハンドラが重複しないこと |

## test_settings.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestSettingsDefaults | test_default_app_name | Settings | 正常系 | デフォルトの app_name が正しいこと |
| TestSettingsDefaults | test_default_env | Settings | 正常系 | デフォルトの env が dev であること |
| TestSettingsDefaults | test_default_log_level | Settings | 正常系 | デフォルトの log_level が INFO であること |
| TestSettingsDefaults | test_default_log_format_contains_common_attributes | Settings | 正常系 | デフォルトの log_format に主要属性が含まれること |
| TestSettingsDefaults | test_default_debug_is_false | Settings | 正常系 | デフォルトの debug が False であること |
| TestSettingsEnvOverride | test_override_log_level | Settings | 正常系 | 環境変数で log_level を上書きできること |
| TestSettingsEnvOverride | test_override_log_format | Settings | 正常系 | 環境変数で log_format を上書きできること |
| TestSettingsEnvOverride | test_override_env | Settings | 正常系 | 環境変数で env を上書きできること |
| TestSettingsEnvOverride | test_override_debug | Settings | 正常系 | 環境変数で debug を上書きできること |
| TestSettingsEnvOverride | test_invalid_env_value_raises | Settings | 異常系 | 不正な env 値で ValidationError が発生すること |
| TestGetSettings | test_returns_settings_instance | get_settings | 正常系 | Settings インスタンスを返すこと |
| TestGetSettings | test_same_instance_on_repeated_calls | get_settings | 正常系 | 繰り返し呼び出しで同一インスタンスを返すこと |
| TestGetSettings | test_cache_clear_creates_new_instance | get_settings | 正常系 | キャッシュクリア後に新しいインスタンスを返すこと |
