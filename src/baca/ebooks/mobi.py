import contextlib
import os
import tempfile
import zipfile
from pathlib import Path

from .. import __appname__
from ..tools import unpack_kindle_book
from .epub import Epub


# TODO:
class Mobi(Epub):
    def __init__(self, ebook_path: Path):
        self._path = ebook_path.resolve()
        self._tempdir = Path(tempfile.mkdtemp(prefix=f"{__appname__}-"))
        with contextlib.redirect_stdout(None):
            unpack_kindle_book(str(self._path), str(self._tempdir), epubver="A", use_hd=True)

    @property
    def _root_dirpath(self) -> Path:
        return self._tempdir / "mobi7"

    @property
    def _version(self) -> str | None:
        return "2.0"

    def get_raw_text(self, content_path: str) -> str:
        with open(content_path, encoding="utf8") as f:
            return f.read()

    def get_toc(self) -> tuple[TocEntry, ...]:
        pass
