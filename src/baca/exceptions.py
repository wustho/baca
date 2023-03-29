from textwrap import dedent

from .utils.systems import VIEWERS
from .utils.user_appdirs import retrieve_user_config_file


class TableDoesNotExist(Exception):
    pass


class BacaException(Exception):
    def __init__(self, message: str):
        super().__init__(f"BacaError: {message}")


class EbookNotFound(BacaException):
    pass


class FormatNotSupported(BacaException):
    pass


class ImageViewerDoesNotExist(BacaException):
    def __init__(self):
        super().__init__(
            dedent(
                f"""\
                Image viewer is missing on your system or isn't configured properly.
                Please make sure any of these image viewers is installed on your systems:
                    {', '.join(VIEWERS)}.

                Or configure your preferred image viewer in: {retrieve_user_config_file()}.
                """
            )
        )
