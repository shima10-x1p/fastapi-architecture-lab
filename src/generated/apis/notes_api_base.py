# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing_extensions import Annotated
from uuid import UUID
from generated.models.add_note_request import AddNoteRequest
from generated.models.error_response import ErrorResponse
from generated.models.http_validation_error import HTTPValidationError
from generated.models.note import Note


class BaseNotesApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseNotesApi.subclasses = BaseNotesApi.subclasses + (cls,)
    async def add_note(
        self,
        bookId: Annotated[UUID, Field(description="書籍の UUID")],
        add_note_request: AddNoteRequest,
    ) -> Note:
        ...
