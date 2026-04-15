# core/adapters/outbound テスト一覧

## test_di.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| TestOutboundAdapterProvider | test_resolves_catalog_port_and_shared_dependencies | OutboundAdapterProvider | 正常系 | dishka の provider から Settings・Cache・CatalogPort を解決できること |
