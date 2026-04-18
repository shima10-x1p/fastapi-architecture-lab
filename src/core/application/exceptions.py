"""application 層で共有する例外定義。"""


class ApplicationError(Exception):
    """
    application 層で扱う基底例外。

    Attributes:
        detail (str): 上位層へ伝搬するエラー詳細。
    """

    def __init__(self, detail: str) -> None:
        """
        例外詳細を保持して初期化する。

        Args:
            detail (str): 上位層へ返すエラー詳細。
        """
        super().__init__(detail)
        self.detail = detail


class AlreadyExistsError(ApplicationError):
    """重複登録を表す application 例外。"""


class NotFoundError(ApplicationError):
    """未存在リソースを表す application 例外。"""
