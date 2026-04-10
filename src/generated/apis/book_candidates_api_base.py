# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing_extensions import Annotated
from generated.models.book_candidate_list_response import BookCandidateListResponse
from generated.models.http_validation_error import HTTPValidationError


class BaseBookCandidatesApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseBookCandidatesApi.subclasses = BaseBookCandidatesApi.subclasses + (cls,)
    async def search_book_candidates(
        self,
        q: Annotated[str, Field(min_length=1, strict=True, description="検索キーワード（タイトル・著者名など）")],
    ) -> BookCandidateListResponse:
        """Open Library の Search API を経由して書籍候補を返す。 結果はキャッシュされる（同一クエリの重複リクエストを抑制するため）。 """
        ...
