# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated.apis.notes_api_base import BaseNotesApi
import generated.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from generated.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field
from typing_extensions import Annotated
from uuid import UUID
from generated.models.add_note_request import AddNoteRequest
from generated.models.error_response import ErrorResponse
from generated.models.http_validation_error import HTTPValidationError
from generated.models.note import Note


router = APIRouter()

ns_pkg = generated.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/v1/books/{bookId}/notes",
    responses={
        201: {"model": Note, "description": "追加されたノート"},
        404: {"model": ErrorResponse, "description": "指定されたリソースが存在しない"},
        422: {"model": HTTPValidationError, "description": "リクエストの形式・バリデーションエラー（FastAPI デフォルト）"},
    },
    tags=["notes"],
    summary="書籍にノートを追加する",
    response_model_by_alias=True,
)
async def add_note(
    bookId: Annotated[UUID, Field(description="書籍の UUID")] = Path(..., description="書籍の UUID"),
    add_note_request: AddNoteRequest = Body(None, description=""),
) -> Note:
    if not BaseNotesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseNotesApi.subclasses[0]().add_note(bookId, add_note_request)
