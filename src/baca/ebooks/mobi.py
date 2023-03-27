import contextlib
import os
import tempfile
import xml.etree.ElementTree as ET
from enum import Enum
from pathlib import Path

from .. import __appname__
from ..models import TocEntry
from ..tools import unpack_kindle_book
from .epub import Epub


class MobiVersion(Enum):
    MOBI7 = "mobi7"
    MOBI8 = "mobi8"


# TODO: test on windows machine
class Mobi(Epub):
    def __init__(self, ebook_path: Path):
        self._path = ebook_path.resolve()
        self._tempdir = Path(tempfile.mkdtemp(prefix=f"{__appname__}-"))
        with contextlib.redirect_stdout(None):
            unpack_kindle_book(str(self._path), str(self._tempdir), epubver="A", use_hd=True)

    @property
    def _mobi_version(self) -> MobiVersion:
        if (self.get_tempdir() / "mobi8").is_dir():
            return MobiVersion.MOBI8
        elif (self.get_tempdir() / "mobi7").is_dir():
            return MobiVersion.MOBI7
        else:
            raise NotImplementedError("Unsupported Mobi version")

    @property
    def _book_dir(self) -> Path:
        return self.get_tempdir() / ("mobi8" if self._mobi_version == MobiVersion.MOBI8 else "mobi7")

    @property
    def _root_filepath(self) -> Path:
        if self._mobi_version == MobiVersion.MOBI8:
            container_file = ET.parse(self._book_dir / "META-INF" / "container.xml")
            rootfile_elem = container_file.find("CONT:rootfiles/CONT:rootfile", Epub.NAMESPACE)
            return self._book_dir / rootfile_elem.attrib["full-path"]  # type: ignore
        else:
            return self._book_dir / "content.opf"

    @property
    def _root_dirpath(self) -> Path:
        return self._root_filepath.parent

    @property
    def _content_opf(self) -> ET.ElementTree:
        return ET.parse(self._root_filepath)

    @property
    def _toc_ncx(self) -> ET.Element:
        toc_ncx_path = self._root_dirpath / self._relactive_toc_ncx_path  # type: ignore
        return ET.parse(toc_ncx_path).getroot()

    def _get_contents(self) -> tuple[str, ...] | tuple[ET.Element, ...]:
        # TODO: using path_resolver kward seems weird, refactor this!
        return Epub._parse_content_opf(self._content_opf, str(self._root_dirpath), path_resolver=os.path.join)

    def get_toc(self) -> tuple[TocEntry, ...]:
        # TODO: using path_resolver kward seems weird, refactor this!
        return Epub._parse_toc(self._toc_ncx, self._version, self._root_dirpath, path_resolver=os.path.join)

    def get_raw_text(self, content_path: str) -> str:
        with open(content_path, encoding="utf8") as f:
            return f.read()

    def get_img_bytestr(self, impath: str) -> tuple[str, bytes]:
        # TODO: test on windows, maybe urljoin?
        # if impath "Images/asdf.png" is problematic
        image_abspath = self._root_dirpath / impath
        image_abspath = os.path.normpath(image_abspath)  # handle crossplatform path
        with open(image_abspath, "rb") as f:
            src = f.read()
        return impath, src
