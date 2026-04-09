# Copilot Instructions — fastapi-architecture-lab

## このリポジトリの目的

Python 3.14 + FastAPI で **Ports and Adapters (Hexagonal Architecture)** を検証する Lab。
動く最短実装よりも、責務の追いやすさ・差し替えやすさ・説明しやすさを優先する。

## ビルド / 実行コマンド

```bash
uv run fastapi dev          # 開発サーバー起動
uv run pytest               # テスト実行
uv run pytest tests/unit    # unit テストのみ
uv run ruff check .         # lint
uv run ruff format .        # format
```

依存管理は **uv** のみ使用。`pip install` は使わない。

## ディレクトリ構成
```
src/
  core/
    domain/               # Entity / Value Object / Enum / Domain Service
    application/
      usecases/           # ユースケース (framework 非依存)
      ports/outbound/     # 外部依存の抽象 (Repository / Gateway / UoW)
    adapters/
      inbound/            # FastAPI router + request/response 変換
      outbound/           # DB実装 / Open Library API呼び出し / キャッシュ
  generated/              # OpenAPI / 外部API 由来の生成モデル
tests/
  unit/                   # usecase / domain の unit テスト
  integration/            # adapter 単体 / router テスト
```

テストは `src/` に混ぜず `tests/` に分離すること（ユーザー設定）。

## アーキテクチャ上の重要ルール

### 依存の方向
```
inbound → usecase → domain
usecase → ports/outbound (抽象)
adapters/outbound → ports/outbound を実装
```
- domain / usecase は FastAPI・Pydantic・HTTP ライブラリに依存しない
- router は薄く保つ。business logic を書かない
- 外部 API レスポンス (`generated/` モデル) を domain や usecase に直接渡さない  
  → `adapters/outbound` 内で内部モデルへ変換してから渡す

### DI パターン
FastAPI の `Depends` を使い、router から直接 `new` しない。

```python
# provider 関数例
def get_book_repository() -> BookRepository: ...
def get_openlibrary_client() -> OpenLibraryClient: ...
def get_search_books_usecase(
    repo: Annotated[BookRepository, Depends(get_book_repository)],
    client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> SearchBooksUsecase: ...
```

テストでは `app.dependency_overrides` で差し替える。

## 主なユースケースとエンドポイント

| ユースケース | エンドポイント |
|------------|--------------|
| 外部書誌検索 | `GET /v1/book-candidates` |
| 書籍取り込み | `POST /v1/books/import` |
| 書籍一覧 | `GET /v1/books` |
| 書籍詳細 | `GET /v1/books/{bookId}` |
| 読書状態更新 | `PATCH /v1/books/{bookId}` |
| ノート追加 | `POST /v1/books/{bookId}/notes` |
| メタデータ再取得 | `POST /v1/books/{bookId}/metadata:refresh` |

HTTP schema (request/response) と domain model は一致させることを前提にしない。

## Open Library 利用ルール

- `User-Agent` を必ず付与: `fastapi-architecture-lab/0.1.0 (contact: your-email@example.com)`
- 同一検索・同一本の取得はキャッシュする
- search 系 API 優先。詳細取得は必要なものだけ
- HTML スクレイピング禁止
- Covers API の一括巡回禁止
- 通信テストは常用しない（fake/stub で代替）

## コーディング規則

- **型ヒント**: Python 3.14 構文を使用。`Annotated` を積極活用
- **モデル**: Pydantic v2 (`model_config`, `model_validator` など v2 API)
- **非同期**: 同期/非同期を途中で混在させない。方針を決めたら一貫させる
- **例外**: domain 例外 / application 例外 / HTTP 例外を層で分ける
- **コメント**: 「なぜそうしているか」を中心に書く（何をしているかはコードで分かる）
- 詳細な Python スタイルは [`.github/instructions/python.instructions.md`](instructions/python.instructions.md) を参照

## 実装順序（新機能追加時の標準手順）

1. `domain/` に Entity / Value Object を定義
2. `ports/outbound/` に抽象インターフェースを定義
3. `usecases/` にユースケースを実装（port を引数で受け取る）
4. `adapters/outbound/` に実装（in-memory 実装から始める）
5. `adapters/inbound/` に router を追加
6. `tests/unit/` に usecase の unit test
7. `tests/integration/` に router テスト

## やってはいけないこと

- 1ファイルに複数層を詰め込む
- router で外部 API を直接呼び出す
- `generated/` モデルを domain model として使い回す
- 永続化モデルをそのまま API response に返す
- Lab なのに最初から複雑な抽象化を積み上げる（まず小さく動かす）
