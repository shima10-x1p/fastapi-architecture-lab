# core/shared テスト一覧

## test_logging.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestGetLogger | test_returns_logger_with_requested_name | get_logger | 正常系 | 指定した名前の Logger を取得できること |
| TestConfigureLogging | test_configures_root_and_handler_levels_from_setting | configure_logging | 正常系/境界値 | 設定したログレベルが大小文字差を吸収して root logger と handler に反映されること |
| TestConfigureLogging | test_replaces_existing_handlers_with_single_stream_handler | configure_logging | 正常系 | 既存 handler を置き換えて単一の StreamHandler を構成すること |
| TestConfigureLogging | test_applies_requested_formatter_to_installed_handler | configure_logging | 正常系 | 設定したフォーマッタが追加された handler に適用されること |
| TestConfigureLogging | test_falls_back_to_info_for_unknown_log_level | configure_logging | 異常系 | 不正なログレベル文字列では INFO にフォールバックすること |
| TestConfigureLogging | test_reconfiguration_keeps_single_handler_and_updates_formatter | configure_logging | 回帰 | 再設定時も handler が増殖せず最新フォーマットへ更新されること |

## test_http_client.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestMergeHeaders | test_allows_extra_headers_to_override_base_headers | merge_headers | 正常系 | 追加ヘッダがベースヘッダを上書きして統合されること |
| TestCreateAsyncClient | test_sets_base_url_timeout_and_default_headers | create_async_client | 正常系 | base_url と timeout とデフォルトヘッダが AsyncClient に設定されること |
| TestSendRequest | test_passes_params_and_headers_to_httpx_client | send_request | 正常系 | クエリパラメータと追加ヘッダが HTTP クライアントへ委譲されること |

## test_settings.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestSettingsInitialization | test_uses_declared_defaults_when_app_env_vars_are_missing | Settings | 正常系 | APP_ 環境変数が未設定のとき定義済みデフォルト値を使うこと |
| TestSettingsInitialization | test_default_log_format_contains_common_logrecord_attributes | Settings | 正常系 | デフォルトの log_format に主要な LogRecord 属性が含まれること |
| TestSettingsInitialization | test_loads_values_from_dotenv_when_environment_is_missing | Settings | 正常系 | 環境変数が未設定なら `.env` の値を読み込むこと |
| TestSettingsInitialization | test_environment_variables_override_dotenv_values | Settings | 正常系 | 環境変数が `.env` より優先されること |
| TestSettingsInitialization | test_allows_app_prefixed_environment_variables_to_override_defaults | Settings | 正常系 | APP_ プレフィックスの環境変数で各設定を上書きできること |
| TestSettingsInitialization | test_ignores_environment_variables_without_app_prefix | Settings | 境界値 | APP_ に似ていてもプレフィックス不一致の環境変数は設定値に影響しないこと |
| TestSettingsInitialization | test_rejects_unknown_env_values | Settings | 異常系 | 許可されていない env 値では ValidationError になること |
| TestGetSettings | test_returns_cached_instance_while_cache_is_warm | get_settings | 正常系 | キャッシュが有効な間は同一インスタンスを返し続けること |
| TestGetSettings | test_reloads_settings_after_cache_clear | get_settings | 正常系 | キャッシュクリア後は最新環境を反映した新しいインスタンスを返すこと |
