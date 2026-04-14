"""アプリケーション層の例外定義。"""


class ApplicationError(Exception):
    """アプリケーション層の基底例外。"""


class InvalidSearchQueryError(ApplicationError):
    """検索クエリが不正な場合の例外。"""
