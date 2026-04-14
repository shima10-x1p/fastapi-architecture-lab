"""core.domain.value_objects.open_library_key のユニットテスト。"""

import pytest

from core.domain.exceptions import InvalidOpenLibraryKeyError
from core.domain.value_objects.open_library_key import OpenLibraryKey


class TestOpenLibraryKey:
    """OpenLibraryKey のフォーマット検証を確認する。"""

    @pytest.mark.parametrize(
        "raw_value",
        [
            "/works/OL45804W",
            "/works/OL1W",
            "/works/OL19809141W",
        ],
    )
    def test_accepts_valid_work_key(self, raw_value: str) -> None:
        # 準備

        # 実行
        key = OpenLibraryKey.from_raw(raw_value)

        # 検証
        assert key.value == raw_value

    @pytest.mark.parametrize(
        "raw_value",
        [
            "",
            "   ",
            "OL45804W",
            "/books/OL7353617M",
            "/works/OL45804W/Fantastic_Mr_Fox",
            "https://openlibrary.org/works/OL45804W",
            "/works/OLABCW",
        ],
    )
    def test_rejects_invalid_work_key(self, raw_value: str) -> None:
        # 準備

        # 実行 / 検証
        with pytest.raises(InvalidOpenLibraryKeyError):
            OpenLibraryKey.from_raw(raw_value)

    def test_returns_work_key_on_str_conversion(self) -> None:
        # 準備
        key = OpenLibraryKey.from_raw("/works/OL45804W")

        # 実行
        actual = str(key)

        # 検証
        assert actual == "/works/OL45804W"
