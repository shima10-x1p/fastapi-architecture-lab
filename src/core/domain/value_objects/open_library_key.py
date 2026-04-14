"""Open Library Work キーを表現する値オブジェクト。"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from core.domain.exceptions import InvalidOpenLibraryKeyError

_WORK_KEY_PATTERN = re.compile(r"^/works/OL\d+W$")


class OpenLibraryKey(BaseModel):
    """Open Library の Work キーを表現する。"""

    model_config = ConfigDict(frozen=True)

    value: str = Field(
        description="Open Library Work キー（例: /works/OL45804W）"
    )

    @field_validator("value")
    @classmethod
    def validate_work_key_format(cls, value: str) -> str:
        """Work キー形式のみを許可する。"""
        if not _WORK_KEY_PATTERN.fullmatch(value):
            raise ValueError("Open Library Work キー形式ではありません。")
        return value

    @classmethod
    def from_raw(cls, raw_value: str) -> OpenLibraryKey:
        """文字列から値オブジェクトを生成する。"""
        try:
            return cls.model_validate({"value": raw_value})
        except ValidationError as exc:
            raise InvalidOpenLibraryKeyError(
                f"不正な Open Library Work キーです: {raw_value!r}"
            ) from exc

    def __str__(self) -> str:
        """文字列表現として Work キーを返す。"""
        return self.value
