# ヘキサゴナルアーキテクチャへのマッピング

このリポジトリ (`fastapi-architecture-lab`) の構造に dishka を対応させる方針。

## Provider の配置ルール

```
src/
  adapters/
    outbound/
      di.py   ← OutboundAdapterProvider (インフラ・Repository実装バインド)
    inbound/
      router.py  ← DishkaRoute / FromDishka を使う
  application/
    di.py     ← UsecaseProvider
```

> `domain/` と `application/usecases/` は Provider を一切知らない。  
> Provider は `adapters/` や `application/` 層のみに置く。

## 依存方向の整合

```
router (inbound)
  → FromDishka[UseCase]
    → UseCase (application) — ポートのみ知っている
      → Port interface (application/ports/outbound/)
        ← Provider が実装 (adapters/outbound/) をバインド
```

## スコープ対応表

| Scope | 用途 |
|-------|------|
| `Scope.APP` | DB コネクションプール、HTTP クライアント（`OpenLibraryClientImpl`）、設定 |
| `Scope.REQUEST` | DB セッション / UoW、認証コンテキスト、各ユースケースインスタンス |

ユースケース自体がステートレスなら `Scope.APP` でも可。

## コード例

```python
# src/adapters/outbound/di.py
from dishka import Provider, provide, Scope
from src.application.ports.outbound.book_repository import BookRepository
from src.application.ports.outbound.book_search_port import BookSearchPort
from src.adapters.outbound.in_memory_book_repository import InMemoryBookRepository
from src.adapters.outbound.openlibrary_client import OpenLibraryClientImpl

class OutboundAdapterProvider(Provider):
    scope = Scope.REQUEST

    # インターフェース(Port) → 実装(Adapter) のバインド
    book_repo     = provide(InMemoryBookRepository, provides=BookRepository)
    search_client = provide(OpenLibraryClientImpl,  provides=BookSearchPort)
```

```python
# src/application/di.py
from dishka import Provider, provide, Scope
from src.application.usecases.search_books import SearchBooksUsecase
from src.application.usecases.import_book  import ImportBookUsecase

class UsecaseProvider(Provider):
    scope = Scope.REQUEST

    # ユースケースの __init__ 型ヒントを自動解析して Port を注入
    search_books = provide(SearchBooksUsecase)
    import_book  = provide(ImportBookUsecase)
```

```python
# src/main.py
def create_container():
    return make_async_container(
        OutboundAdapterProvider(),
        UsecaseProvider(),
        FastapiProvider(),
    )
```

## 実装追加時の標準手順（dishka版）

1. `domain/` に Entity / Value Object を定義
2. `application/ports/outbound/` に抽象 Port を定義
3. `application/usecases/` にユースケースを実装（Port を引数型ヒントで受け取る）
4. `adapters/outbound/` に Port 実装を追加
5. `adapters/outbound/di.py` の `OutboundAdapterProvider` にバインドを追加
6. `application/di.py` の `UsecaseProvider` にユースケースを追加
7. `adapters/inbound/router.py` に `FromDishka[NewUsecase]` でエンドポイントを追加
