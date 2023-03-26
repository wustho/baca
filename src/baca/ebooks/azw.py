import contextlib
import os
import zipfile
from pathlib import Path

from ..tools import unpack_kindle_book
from ..utils.tempdir import create_tempdir
from .epub import Epub


class Azw(Epub):
    def __init__(self, ebook_path: Path):
        self._path = ebook_path.resolve()
        self._tempdir = create_tempdir()
        self._tmpepub = self._tempdir / "mobi8" / f"{os.path.splitext(self._path)[0]}.epub"
        with contextlib.redirect_stdout(None):
            unpack_kindle_book(str(self._path), str(self._tempdir), epubver="A", use_hd=True)
        self._file = zipfile.ZipFile(self._tmpepub, "r")
