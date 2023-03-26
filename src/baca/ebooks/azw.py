import contextlib
import os
import tempfile
from pathlib import Path
import zipfile

from .. import __appname__
from ..tools import unpack_kindle_book
from .epub import Epub


class Azw(Epub):
    def __init__(self, fileepub: Path):
        self._path = fileepub.resolve()
        self._tempdir = Path(tempfile.mkdtemp(prefix=f"{__appname__}-"))
        self._tmpepub = self._tempdir / "mobi8" / f"{os.path.splitext(self._path)[0]}.epub"
        with contextlib.redirect_stdout(None):
            unpack_kindle_book(str(self._path), str(self._tempdir), epubver="A", use_hd=True)
        self._file = zipfile.ZipFile(self._tmpepub, "r")
