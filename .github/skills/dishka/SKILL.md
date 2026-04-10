---
name: dishka
description: 'dishka DI コンテナを Python FastAPI プロジェクトに導入・設定するワークフロー。Use when: DIフレームワーク dishka の導入、Provider/Container/Scope の定義、FastAPI との統合 (DishkaRoute, FromDishka, setup_dishka)、ヘキサゴナルアーキテクチャへの対応、テスト用コンテナの構成。dishka install integration scope provider container lifespan inject dependency injection hexagonal architecture'
argument-hint: '対象 (例: FastAPI統合, スコープ設計, テスト, ヘキサゴナルアーキテクチャ)'
---

# dishka — DI Framework

Python 3.14 + FastAPI + Hexagonal Architecture に dishka を統合するスキル。

## いつ使うか

- `dishka` を新規プロジェクトに導入・設定するとき
- `Provider` / `Scope` の設計・実装を行うとき
- FastAPI エンドポイントへの `FromDishka[T]` / `DishkaRoute` を組み込むとき
- Hexagonal Architecture の各層への Provider 配置を整理したいとき
- テスト用コンテナを組み立てて依存を差し替えたいとき

## セットアップ手順

### 1. インストール

```bash
uv add "dishka[fastapi]"
```

### 2. Provider を定義する

| ファイル | Provider クラス | 担当 |
|---------|----------------|------|
| `src/adapters/outbound/di.py` | `OutboundAdapterProvider` | Repository 実装 → Port バインド、HTTP クライアント |
| `src/application/di.py` | `UsecaseProvider` | ユースケースクラス |

スコープの判断基準：
- `Scope.APP` — DB プール、HTTP クライアント、設定（アプリ全体で1インスタンス）
- `Scope.REQUEST` — DB セッション、UoW、各ユースケース（リクエストごとに初期化が必要なもの）

```python
# src/adapters/outbound/di.py
from dishka import Provider, provide, Scope
from src.application.ports.outbound.book_repository import BookRepository
from src.adapters.outbound.in_memory_book_repository import InMemoryBookRepository

class OutboundAdapterProvider(Provider):
    scope = Scope.REQUEST
    book_repo = provide(InMemoryBookRepository, provides=BookRepository)
```

```python
# src/application/di.py
from dishka import Provider, provide, Scope
from src.application.usecases.search_books import SearchBooksUsecase

class UsecaseProvider(Provider):
    scope = Scope.REQUEST
    search_books = provide(SearchBooksUsecase)
```

### 3. Router に DishkaRoute を設定し FromDishka で注入

```python
# src/adapters/inbound/router.py
from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from src.application.usecases.search_books import SearchBooksUsecase

router = APIRouter(route_class=DishkaRoute)

@router.get("/v1/book-candidates")
async def search_books(
    q: str,
    usecase: FromDishka[SearchBooksUsecase],
) -> list[BookCandidateResponse]:
    return await usecase.execute(query=q)
```

### 4. アプリにコンテナを接続

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app

def create_container():
    return make_async_container(
        OutboundAdapterProvider(),
        UsecaseProvider(),
        FastapiProvider(),  # Request/WebSocket を提供する組み込み Provider
    )

app = create_app()
setup_dishka(container=create_container(), app=app)
```

## 主要シンボル早見表

| 用途 | シンボル |
|------|---------|
| ファクトリ宣言 | `@provide(scope=Scope.X)` |
| インターフェースバインド | `provide(Impl, provides=Port, scope=...)` |
| yield ファイナライズ | `async def f(...) -> AsyncIterable[T]: yield obj` |
| エンドポイント注入 | `param: FromDishka[T]` |
| 自動 inject 付き Router | `APIRouter(route_class=DishkaRoute)` |
| アプリ接続 | `setup_dishka(container, app)` |
| テスト時上書き | `@provide(..., override=True)` |

## よくある落とし穴

- `domain/` や `application/usecases/` に `Provider` をインポートしない（層境界違反）
- `APP` スコープが `REQUEST` スコープのものに依存させると起動時バリデーションエラー
- WebSocket エンドポイントには `DishkaRoute` が効かず `@inject` を手動付与
- `from_context` のキーは生の型のみ（`Annotated[T, ...]` 不可）
- テスト後に `container.close()` を呼ばないと DB 接続等がリークする

## 詳細リファレンス

- [FastAPI 統合・高度なパターン](./references/integration.md)
- [ヘキサゴナルアーキテクチャへのマッピング](./references/architecture.md)
- [テストパターン](./references/testing.md)
