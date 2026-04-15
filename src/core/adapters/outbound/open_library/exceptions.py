"""Open Library adapter 専用の例外定義。"""


class OpenLibraryAdapterError(Exception):
    """Open Library adapter の基底例外。"""


class OpenLibraryNotFoundError(OpenLibraryAdapterError):
    """対象リソースが Open Library 側に存在しない場合の例外。"""


class OpenLibraryRateLimitError(OpenLibraryAdapterError):
    """Open Library のレート制限に到達した場合の例外。"""


class OpenLibraryTransportError(OpenLibraryAdapterError):
    """Open Library との通信に失敗した場合の例外。"""


class OpenLibraryPayloadError(OpenLibraryAdapterError):
    """Open Library のレスポンス形式が期待と異なる場合の例外。"""
