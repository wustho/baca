import dataclasses
import contextlib
import os
import xml.etree.ElementTree as ET
import tempfile
import zipfile
from pathlib import Path

from .. import __appname__
from ..tools import unpack_kindle_book
from .epub import Epub
from ..models import BookMetadata, Segment, TocEntry


# TODO:
class Mobi(Epub):
    def __init__(self, ebook_path: Path):
        self._path = ebook_path.resolve()
        self._tempdir = Path(tempfile.mkdtemp(prefix=f"{__appname__}-"))
        with contextlib.redirect_stdout(None):
            unpack_kindle_book(str(self._path), str(self._tempdir), epubver="A", use_hd=True)

    @property
    def _root_dirpath(self) -> str:
        # TODO:
        return os.path.join(self._tempdir, "mobi7") + "/"  # to workaround urljoin, careful on Windows!

    @property
    def _version(self) -> str:
        return "2.0"

    @property
    def _content_opf(self) -> ET.ElementTree:
        with open(os.path.join(self._root_dirpath, "content.opf")) as f:
            return ET.parse(f)  # .getroot()

    def get_raw_text(self, content_path: str) -> str:
        with open(content_path, encoding="utf8") as f:
            return f.read()

    def get_toc(self) -> tuple[TocEntry, ...]:
        toc_path = os.path.join(self._root_dirpath, "toc.ncx")
        with open(toc_path) as f:
            toc = ET.parse(f).getroot()
        return Epub._parse_toc(toc, self._version, self._root_dirpath)  # *self.contents (absolute path)

    def get_img_bytestr(self, impath: str) -> tuple[str, bytes]:
        # TODO: test on windows, maybe urljoin?
        # if impath "Images/asdf.png" is problematic
        image_abspath = os.path.join(self._root_dirpath, impath)
        image_abspath = os.path.normpath(image_abspath)  # handle crossplatform path
        with open(image_abspath, "rb") as f:
            src = f.read()
        return impath, src
