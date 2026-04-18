"""ドメイン層とアプリケーション層で共有する例外定義。"""


class DomainError(Exception):
    """ドメインルール違反を表す基底例外。"""

    message: str

    def __init__(self, message: str) -> None:
        """
        例外メッセージを保持して初期化する。

        Args:
            message (str): 呼び出し元へ伝える例外メッセージ。
        """
        self.message = message
        super().__init__(message)


class ApplicationError(Exception):
    """アプリケーション層の失敗を表す基底例外。"""

    message: str
    resource_id: str | None

    def __init__(
        self,
        message: str,
        resource_id: str | None = None,
    ) -> None:
        """
        例外メッセージと対象リソース識別子を保持して初期化する。

        Args:
            message (str): 呼び出し元へ伝える例外メッセージ。
            resource_id (str | None): 関連するリソース識別子。

        Exceptions:
            ValueError: resource_id が空文字列、または空白のみの場合に発生。
        """
        self.message = message
        self.resource_id = _normalize_resource_id(resource_id)
        super().__init__(message)


class NotFoundError(ApplicationError):
    """対象リソースが見つからないことを表す例外。"""

    def __init__(self, resource_id: str, message: str | None = None) -> None:
        """
        見つからないリソースを表す例外を初期化する。

        Args:
            resource_id (str): 見つからなかったリソース識別子。
            message (str | None): 明示指定時に利用する例外メッセージ。

        Exceptions:
            ValueError: resource_id が空文字列、または空白のみの場合に発生。
        """
        normalized_resource_id = _require_resource_id(resource_id)
        resolved_message = message or (
            f"指定されたリソースが見つかりません: {normalized_resource_id}"
        )
        super().__init__(resolved_message, resource_id=normalized_resource_id)


class ConflictError(ApplicationError):
    """対象リソースの競合を表す例外。"""

    def __init__(self, resource_id: str, message: str | None = None) -> None:
        """
        リソース競合を表す例外を初期化する。

        Args:
            resource_id (str): 競合したリソース識別子。
            message (str | None): 明示指定時に利用する例外メッセージ。

        Exceptions:
            ValueError: resource_id が空文字列、または空白のみの場合に発生。
        """
        normalized_resource_id = _require_resource_id(resource_id)
        resolved_message = message or (
            f"指定されたリソースはすでに存在します: {normalized_resource_id}"
        )
        super().__init__(resolved_message, resource_id=normalized_resource_id)


def _normalize_resource_id(resource_id: str | None) -> str | None:
    """
    リソース識別子を検証し、利用可能な形へ正規化する。

    Args:
        resource_id (str | None): 検証対象のリソース識別子。

    Returns:
        str | None: 利用可能なリソース識別子。未指定時は None。

    Exceptions:
        ValueError: resource_id が空文字列、または空白のみの場合に発生。
    """
    if resource_id is None:
        return None

    normalized_resource_id = resource_id.strip()
    if not normalized_resource_id:
        raise ValueError("resource_id に空文字列や空白のみは指定できません。")

    return normalized_resource_id


def _require_resource_id(resource_id: str) -> str:
    """
    必須のリソース識別子を検証して返す。

    Args:
        resource_id (str): 検証対象のリソース識別子。

    Returns:
        str: 検証済みのリソース識別子。

    Exceptions:
        ValueError: resource_id が空文字列、または空白のみの場合に発生。
    """
    normalized_resource_id = _normalize_resource_id(resource_id)
    if normalized_resource_id is None:
        raise ValueError("resource_id は必須です。")

    return normalized_resource_id
