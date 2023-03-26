from textwrap import dedent

from .utils.systems import VIEWERS
from .utils.user_appdirs import retrieve_user_config_file


class TableDoesNotExist(Exception):
    pass


class ImageViewerDoesNotExist(Exception):
    def __init__(self):
        super().__init__(
            dedent(
                f"""
                Error: Image viewer is missing on your system or isn't configured properly.
                Please make sure any of this image viewer is installed on your systems:
                    {', '.join(VIEWERS)}.

                Or configure your preferred image viewer in: {retrieve_user_config_file()}.
                """
            )
        )
