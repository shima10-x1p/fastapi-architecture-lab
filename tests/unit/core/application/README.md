# core/application テスト一覧

## test_exceptions.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestApplicationErrors | test_application_error_preserves_detail_in_message | ApplicationError | 正常系 | detail を属性と文字列表現の両方で保持すること |
| TestApplicationErrors | test_specialized_errors_preserve_detail_and_inherit_application_error | AlreadyExistsError / NotFoundError | 正常系 | 派生例外も detail を保持し ApplicationError として扱えること |
