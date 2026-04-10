# FastAPI 統合 — 高度なパターン

## `@inject` を手動で使う場合

`DishkaRoute` を使わないルーターや WebSocket では手動で付ける：

```python
from dishka.integrations.fastapi import inject

@router.websocket("/ws")
@inject
async def websocket_endpoint(ws: WebSocket, handler: FromDishka[MessageHandler]) -> None:
    await ws.accept()
    ...
```

## `Depends` と dishka の混在

dishka 管理の依存を FastAPI `Depends` 関数の中で使う場合、`DishkaRoute` ルーターでも `@inject` を手動付与が必要：

```python
from dishka.integrations.fastapi import inject

@inject  # DishkaRoute 配下でも Depends 関数には手動で付ける
async def get_current_user(
    gateway: FromDishka[UserGateway],
    token: str = Depends(oauth2_scheme),
) -> User:
    return await gateway.find_by_token(token)

@router.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    ...
```

## yield ファクトリによる自動ファイナライズ

スコープ終了時に `yield` 後のコードが自動実行される：

```python
class OutboundAdapterProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_db_session(self, pool: Pool) -> AsyncIterable[Session]:
        async with pool.session() as session:
            yield session
        # yield 後: スコープ終了時に自動実行（commit/rollback など）
```

## `from_context` — スコープ進入時の外部データ注入

```python
class MyProvider(Provider):
    app_config = from_context(provides=AppConfig, scope=Scope.APP)

# コンテナ作成時に APP レベルのコンテキストを渡す
container = make_async_container(MyProvider(), context={AppConfig: config})
```

> キーは `Annotated[T, ...]` ではなく**生の型**を使う。

## `AnyOf` — 1ファクトリで複数型を提供

```python
from dishka import AnyOf

class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_client(self) -> AnyOf[OpenLibraryClientImpl, BookSearchPort]:
        return OpenLibraryClientImpl()
    # container.get(OpenLibraryClientImpl) == container.get(BookSearchPort)
```

## `alias` — 同一オブジェクトを別の型でも取得

```python
class MyProvider(Provider):
    book_repo_impl = provide(SqlBookRepository, scope=Scope.REQUEST)
    book_repo      = alias(source=SqlBookRepository, provides=BookRepository)
```

## バリデーション設定

```python
from dishka import STRICT_VALIDATION

container = make_async_container(
    ...,
    validation_settings=STRICT_VALIDATION,
)
```
