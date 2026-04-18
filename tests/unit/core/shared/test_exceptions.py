"""共有例外ユーティリティの unit test。"""

import pytest

import core.shared as shared_module
from core.shared.exceptions import (
    ApplicationError,
    ConflictError,
    DomainError,
    NotFoundError,
)


def test_domain_error_stores_message_and_returns_it_from_str() -> None:
    """DomainError が message 属性と文字列表現へ同じ値を保持する。"""

    # 準備
    message = "ドメインルールに違反しました。"

    # 実行
    error = DomainError(message)

    # 検証
    assert error.message == message
    assert str(error) == message


def test_application_error_stores_message_without_resource_id() -> None:
    """ApplicationError は resource_id 未指定時に None を保持する。"""

    # 準備
    message = "アプリケーションエラーが発生しました。"

    # 実行
    error = ApplicationError(message)

    # 検証
    assert error.message == message
    assert error.resource_id is None
    assert str(error) == message


def test_application_error_stores_message_and_resource_id() -> None:
    """ApplicationError は指定された resource_id を保持する。"""

    # 準備
    message = "対象リソースの処理に失敗しました。"
    resource_id = "book-001"

    # 実行
    error = ApplicationError(message, resource_id=resource_id)

    # 検証
    assert error.message == message
    assert error.resource_id == resource_id
    assert str(error) == message


def test_not_found_error_uses_default_message_when_message_is_omitted() -> None:
    """NotFoundError は既定メッセージへ resource_id を含める。"""

    # 準備
    resource_id = "book-001"

    # 実行
    error = NotFoundError(resource_id)

    # 検証
    assert error.resource_id == resource_id
    assert error.message == f"指定されたリソースが見つかりません: {resource_id}"
    assert str(error) == error.message


def test_conflict_error_uses_default_message_when_message_is_omitted() -> None:
    """ConflictError は既定メッセージへ resource_id を含める。"""

    # 準備
    resource_id = "book-001"

    # 実行
    error = ConflictError(resource_id)

    # 検証
    assert error.resource_id == resource_id
    assert error.message == f"指定されたリソースはすでに存在します: {resource_id}"
    assert str(error) == error.message


def test_not_found_error_accepts_message_override() -> None:
    """NotFoundError は明示したメッセージを優先する。"""

    # 準備
    resource_id = "book-001"
    message = "書籍が見つかりません。"

    # 実行
    error = NotFoundError(resource_id, message=message)

    # 検証
    assert error.resource_id == resource_id
    assert error.message == message
    assert str(error) == message


def test_conflict_error_accepts_message_override() -> None:
    """ConflictError は明示したメッセージを優先する。"""

    # 準備
    resource_id = "book-001"
    message = "書籍 ID が重複しています。"

    # 実行
    error = ConflictError(resource_id, message=message)

    # 検証
    assert error.resource_id == resource_id
    assert error.message == message
    assert str(error) == message


@pytest.mark.parametrize("resource_id", ["", "   "])
def test_application_error_raises_value_error_for_blank_resource_id(
    resource_id: str,
) -> None:
    """ApplicationError は空文字列と空白のみの resource_id を拒否する。"""

    # 準備
    message = "対象リソースの処理に失敗しました。"

    # 実行 / 検証
    with pytest.raises(ValueError, match="resource_id"):
        ApplicationError(message, resource_id=resource_id)


@pytest.mark.parametrize("resource_id", ["", "   "])
def test_not_found_error_raises_value_error_for_blank_resource_id(
    resource_id: str,
) -> None:
    """NotFoundError は空文字列と空白のみの resource_id を拒否する。"""

    # 実行 / 検証
    with pytest.raises(ValueError, match="resource_id"):
        NotFoundError(resource_id)


@pytest.mark.parametrize("resource_id", ["", "   "])
def test_conflict_error_raises_value_error_for_blank_resource_id(
    resource_id: str,
) -> None:
    """ConflictError は空文字列と空白のみの resource_id を拒否する。"""

    # 実行 / 検証
    with pytest.raises(ValueError, match="resource_id"):
        ConflictError(resource_id)


def test_not_found_error_and_conflict_error_are_application_error_instances() -> None:
    """NotFoundError と ConflictError が ApplicationError を継承する。"""

    # 準備
    not_found_error = NotFoundError("book-001")
    conflict_error = ConflictError("book-001")

    # 検証
    assert isinstance(not_found_error, ApplicationError)
    assert isinstance(conflict_error, ApplicationError)


def test_domain_error_is_not_an_application_error() -> None:
    """DomainError が ApplicationError とは別系統の例外である。"""

    # 準備
    error = DomainError("ドメインルールに違反しました。")

    # 検証
    assert isinstance(error, DomainError)
    assert not isinstance(error, ApplicationError)


def test_core_shared_re_exports_exception_classes() -> None:
    """core.shared が共有例外クラスを再公開している。"""

    # 検証
    assert shared_module.ApplicationError is ApplicationError
    assert shared_module.ConflictError is ConflictError
    assert shared_module.DomainError is DomainError
    assert shared_module.NotFoundError is NotFoundError
