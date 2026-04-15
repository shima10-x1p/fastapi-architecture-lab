# core/adapters/outbound/open_library テスト一覧

## test_cache.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestOpenLibraryCache | test_returns_none_for_missing_search_cache | OpenLibraryCache | 正常系 | 未登録の検索クエリではキャッシュが存在しないこと |
| TestOpenLibraryCache | test_returns_cached_search_candidates_before_expiry | OpenLibraryCache | 正常系/境界値 | TTL 以内では検索結果をそのまま返すこと |
| TestOpenLibraryCache | test_expires_cached_search_candidates_after_ttl | OpenLibraryCache | 境界値 | TTL 超過後は検索キャッシュを無効化すること |
| TestOpenLibraryCache | test_keeps_search_and_metadata_entries_separate | OpenLibraryCache | 正常系 | 検索結果とメタデータのキャッシュ領域が分離されていること |

## test_catalog_adapter.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestSearchBookCandidates | test_uses_cache_before_sending_http_request | OpenLibraryCatalogAdapter.search_book_candidates | 正常系/回帰 | 検索結果がキャッシュ済みなら HTTP リクエストを送らないこと |
| TestSearchBookCandidates | test_fetches_and_caches_search_results | OpenLibraryCatalogAdapter.search_book_candidates | 正常系 | 検索結果を取得してキャッシュし、同一クエリの再取得では再利用すること |
| TestSearchBookCandidates | test_raises_rate_limit_error_on_429_response | OpenLibraryCatalogAdapter.search_book_candidates | 異常系 | 429 応答をレート制限例外へ変換すること |
| TestSearchBookCandidates | test_raises_transport_error_on_timeout | OpenLibraryCatalogAdapter.search_book_candidates | 異常系 | タイムアウトを通信例外へ変換すること |
| TestFetchBookMetadata | test_fetches_work_authors_and_editions_then_caches_result | OpenLibraryCatalogAdapter.fetch_book_metadata | 正常系 | work・author・editions を統合したメタデータを取得してキャッシュすること |
| TestFetchBookMetadata | test_raises_not_found_error_on_404_response | OpenLibraryCatalogAdapter.fetch_book_metadata | 異常系 | 404 応答を未検出例外へ変換すること |

## test_mapper.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestBuildCoverUrl | test_returns_cover_url_when_cover_id_exists | build_cover_url | 正常系 | cover_id から Covers API の画像 URL を組み立てられること |
| TestBuildCoverUrl | test_returns_none_when_cover_id_is_missing | build_cover_url | 境界値 | cover_id がない場合は URL を返さないこと |
| TestMapSearchPayload | test_maps_valid_search_documents_to_book_candidates | map_search_payload | 正常系 | 妥当な search payload を検索候補一覧へ変換できること |
| TestMapSearchPayload | test_skips_invalid_search_documents | map_search_payload | 異常系/回帰 | 不正な doc が含まれていても有効な候補だけを残すこと |
| TestExtractAuthorKeys | test_extracts_author_keys_from_work_payload | extract_author_keys | 正常系 | work payload から author key 一覧を抽出できること |
| TestSelectBestEdition | test_prefers_edition_with_richer_metadata | select_best_edition | 正常系 | 情報量の多い edition を優先して選択すること |
| TestMapBookMetadata | test_combines_work_author_and_edition_payloads | map_book_metadata | 正常系 | work・author・edition の payload を統合して内部メタデータへ変換できること |
| TestMapBookMetadata | test_raises_error_when_author_names_cannot_be_resolved | map_book_metadata | 異常系 | 著者名を解決できない場合は payload 例外を送出すること |
