"""core.application.di のユニットテスト。"""

import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from dishka import make_async_container

from core.adapters.outbound.di import OutboundAdapterProvider
from core.application.di import UsecaseProvider
from core.application.usecases.search_book_candidates import (
    SearchBookCandidatesUsecase,
)
from core.shared.settings import get_settings


@pytest.fixture(autouse=True)
def isolate_usecase_provider_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[None]:
    """dishka provider テスト用に settings を隔離する。"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_OPEN_LIBRARY_CONTACT_EMAIL", "test@example.com")
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


class TestUsecaseProvider:
    """UsecaseProvider が検索ユースケースを解決できることを検証する。"""

    def test_resolves_search_book_candidates_usecase(self) -> None:
        # 準備

        async def exercise() -> SearchBookCandidatesUsecase:
            container = make_async_container(
                OutboundAdapterProvider(),
                UsecaseProvider(),
            )
            try:
                async with container() as request_container:
                    return await request_container.get(
                        SearchBookCandidatesUsecase
                    )
            finally:
                await container.close()

        # 実行
        usecase = asyncio.run(exercise())

        # 検証
        assert isinstance(usecase, SearchBookCandidatesUsecase)
