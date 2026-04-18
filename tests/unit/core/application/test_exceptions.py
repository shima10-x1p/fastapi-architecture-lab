"""application 例外の unit test。"""

from __future__ import annotations

import pytest

from core.application.exceptions import (
    AlreadyExistsError,
    ApplicationError,
    NotFoundError,
)


class TestApplicationErrors:
    """application 例外の基本挙動を確認する。"""

    def test_application_error_preserves_detail_in_message(self) -> None:
        """detail を属性と文字列表現の両方で保持する。"""
        # Arrange
        detail = "validation failed"

        # Act
        error = ApplicationError(detail)

        # Assert
        assert error.detail == detail
        assert str(error) == detail

    @pytest.mark.parametrize("error_class", [AlreadyExistsError, NotFoundError])
    def test_specialized_errors_preserve_detail_and_inherit_application_error(
        self,
        error_class: type[ApplicationError],
    ) -> None:
        """派生例外も detail を保持し基底例外として扱える。"""
        # Arrange
        detail = "specific error"

        # Act
        error = error_class(detail)

        # Assert
        assert isinstance(error, ApplicationError)
        assert error.detail == detail
        assert str(error) == detail
