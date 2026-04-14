# core/application/usecases テスト一覧

## test_search_book_candidates.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestSearchBookCandidatesUsecase | test_trims_query_before_delegating_to_port | SearchBookCandidatesUsecase | 正常系/境界値 | 検索語の前後空白を除去して port に委譲できること |
| TestSearchBookCandidatesUsecase | test_raises_error_when_query_is_blank_after_trim | SearchBookCandidatesUsecase | 異常系/境界値 | trim 後に空になる検索語を拒否して例外を送出すること |
| TestSearchBookCandidatesUsecase | test_returns_domain_models_without_conversion | SearchBookCandidatesUsecase | 回帰 | port から返る domain model を変換せずそのまま返すこと |
