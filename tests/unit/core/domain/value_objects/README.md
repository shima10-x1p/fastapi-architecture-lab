# core/domain/value_objects テスト一覧

## test_open_library_key.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestOpenLibraryKey | test_accepts_valid_work_key | OpenLibraryKey | 正常系 | Work キー形式の入力を受理して値オブジェクトを生成できること |
| TestOpenLibraryKey | test_rejects_invalid_work_key | OpenLibraryKey | 異常系/境界値 | 空文字や Work キー以外の形式を受理せず例外を送出すること |
| TestOpenLibraryKey | test_returns_work_key_on_str_conversion | OpenLibraryKey | 正常系 | 値オブジェクトの文字列表現で元の Work キーを取得できること |
