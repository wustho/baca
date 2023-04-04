class TableDoesNotExist(Exception):
    pass


class BacaException(Exception):
    def __init__(self, message: str):
        super().__init__(f"BacaError: {message}")


class EbookNotFound(BacaException):
    pass


class FormatNotSupported(BacaException):
    pass


class LaunchingFileError(Exception):
    pass
