# テストパターン

## 基本方針

- コンテナはグローバルではなく**テストごとに生成**する
- 本番 Provider と MockProvider を組み合わせる
- `override=True` で特定依存を差し替える
- `create_app()` と `create_container()` を分離しておくと差し替えが簡単
- テスト後は必ず `container.close()` を呼ぶ（ファイナライズ・接続リーク防止）

## pytest フィクスチャパターン

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka

class MockBookRepositoryProvider(Provider):
    @provide(scope=Scope.APP, override=True)
    def get_repo(self) -> BookRepository:
        return InMemoryBookRepository()

@pytest_asyncio.fixture
async def container():
    c = make_async_container(
        OutboundAdapterProvider(),         # 本番の一部はそのまま使う
        MockBookRepositoryProvider(),      # 差し替えたいものだけ上書き
        UsecaseProvider(),
        FastapiProvider(),
    )
    yield c
    await c.close()  # 必須: ファイナライズを実行

@pytest.fixture
def client(container):
    app = create_app()
    setup_dishka(container, app)
    with TestClient(app) as c:
        yield c
```

## コンテナから直接取得（ユニットテスト相当）

```python
@pytest.mark.asyncio
async def test_usecase(container):
    async with container() as req_container:
        usecase = await req_container.get(SearchBooksUsecase)
        result = await usecase.execute(query="Python")
    assert len(result) > 0
```

## 統合テスト例（ルーターテスト）

```python
# tests/integration/test_books_router.py
@pytest.mark.asyncio
async def test_list_books(client: TestClient, container):
    # コンテナから直接 Repository を取り出してデータを仕込む
    async with container() as req_container:
        repo = await req_container.get(BookRepository)
    await repo.save(Book(id=BookId("1"), title="Clean Code"))

    response = client.get("/v1/books")
    assert response.status_code == 200
    assert len(response.json()) == 1
```

## `from_context` を override に使う

本番は `provide(Config)` だがテストは外部から注入したい場合：

```python
from dishka import from_context

class TestConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=AppConfig, override=True)

test_container = make_async_container(
    MainProvider(),
    TestConfigProvider(),
    context={AppConfig: AppConfig(database_url="sqlite+aiosqlite:///:memory:")},
)
```
