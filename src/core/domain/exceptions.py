"""ドメイン層の例外定義。"""


class DomainError(Exception):
    """ドメイン層の基底例外。"""


class InvalidOpenLibraryKeyError(DomainError):
    """Open Library Work キーが不正な場合の例外。"""
