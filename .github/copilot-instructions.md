# Copilot Instructions — fastapi-architecture-lab

## このリポジトリの目的

Python 3.14 + FastAPI で **Ports and Adapters (Hexagonal Architecture)** を検証する Lab。
お気に入り YouTube 動画の管理と、埋め込みプレイヤー HTML の取得を提供する。
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
      ports/outbound/     # 外部依存の抽象 (Repository など)
    adapters/
      inbound/            # FastAPI router + request/response 変換
      outbound/           # CSV / SQLite / S3 など保存先の実装
  generated/              # OpenAPI Generator による自動生成コード（編集禁止）
tests/
  unit/                   # usecase / domain の unit テスト
  integration/            # adapter 単体 / router テスト
```

テストは `src/` に混ぜず `tests/` に分離すること（ユーザー設定）。

### テストのディレクトリ構成

`tests/unit/` および `tests/integration/` 配下は **`src/` と同じ階層構造**を維持する。

```
src/core/shared/settings.py
→ tests/unit/core/shared/test_settings.py

src/core/application/usecases/search_books.py
→ tests/unit/core/application/usecases/test_search_books.py
```

テストファイルを新規作成するときは、対応する `src/` のパスに合わせてディレクトリを切ること。

## アーキテクチャ上の重要ルール

### 依存の方向
```
inbound → usecase → domain
usecase → ports/outbound (抽象)
adapters/outbound → ports/outbound を実装
```
- domain / usecase は FastAPI・Pydantic・HTTP ライブラリに依存しない
- router は薄く保つ。business logic を書かない
- 保存先（CSV / SQLite / S3 等）は `ports/outbound` の抽象を介してアクセスし、`adapters/outbound` で実装する

### DI パターン
FastAPI の `Depends` を使い、router から直接 `new` しない。

```python
# provider 関数例
def get_favorite_repository() -> FavoriteRepository: ...
def get_add_favorite_usecase(
    repo: Annotated[FavoriteRepository, Depends(get_favorite_repository)],
) -> AddFavoriteUsecase: ...
```

テストでは `app.dependency_overrides` で差し替える。

## 主なユースケースとエンドポイント

| ユースケース | エンドポイント |
|------------|--------------|
| お気に入り追加 | `POST /v1/favorites` |
| お気に入り一覧取得 | `GET /v1/favorites` |
| お気に入り単体取得 | `GET /v1/favorites/{videoId}` |
| お気に入り更新 | `PATCH /v1/favorites/{videoId}` |
| お気に入り削除 | `DELETE /v1/favorites/{videoId}` |
| 埋め込みプレイヤー取得 | `GET /v1/favorites/{videoId}/embed` |

HTTP schema (request/response) と domain model は一致させることを前提にしない。

## 保存先の差し替え

お気に入りの保存先は DI で差し替え可能にする。以下は今回の Lab で検証する候補の例。

- **CSV ファイル**: 最初の実装として使うシンプルな保存先
- **SQLite**: ローカル DB による永続化
- **S3**: クラウドストレージへの保存

`FavoriteRepository` の抽象インターフェースを定義し、各保存先の adapter を実装する。

## コーディング規則

- **型ヒント**: Python 3.14 構文を使用。`Annotated` を積極活用
- **モデル**: Pydantic v2 (`model_config`, `model_validator` など v2 API)
- **非同期**: 同期/非同期を途中で混在させない。方針を決めたら一貫させる
- **例外**: domain 例外 / application 例外 / HTTP 例外を層で分ける
- **コメント / docstring の言語**: このプロジェクトではコメント・docstringを日本語で記述する
- **コメント**: 「何をしているか」は最小限・処理が追える程度に書く。「なぜそうしているか」を中心に書く
- 詳細な Python スタイルは [`.github/instructions/python.instructions.md`](instructions/python.instructions.md) を参照

### docstring の例

```python
def example_function(param1: int, param2: str) -> bool:
    """
    例示用の関数

    Args:
        param1 (int): 整数のパラメータ
        param2 (str): 文字列のパラメータ

    Returns:
        bool: 処理結果

    Exceptions:
        ValueError: param1 が負の値の場合に発生
        TypeError: param2 が空文字列の場合に発生
    """
    return True

## 実装順序（新機能追加時の標準手順）

1. `domain/` に Entity / Value Object を定義
2. `ports/outbound/` に抽象インターフェースを定義
3. `usecases/` にユースケースを実装（port を引数で受け取る）
4. `adapters/outbound/` に実装（in-memory 実装から始める）
5. `adapters/inbound/` に router を追加
6. `tests/unit/core/...` に usecase の unit test（`src/` と同じ階層）
7. `tests/integration/core/...` に router テスト（`src/` と同じ階層）

## やってはいけないこと

- 1ファイルに複数層を詰め込む
- router で保存先を直接操作する（必ず usecase / port 経由）
- 永続化モデルをそのまま API response に返す
- Lab なのに最初から複雑な抽象化を積み上げる（まず小さく動かす）
- `src/generated/` 配下のファイルを手動編集する（OpenAPI Generator で再生成するため上書きされる）
