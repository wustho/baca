import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from ..models import BookMetadata, Segment, TocEntry


class Ebook:
    def __init__(self, ebook_path: Path):
        raise NotImplementedError()

    def get_tempdir(self) -> Path:
        raise NotImplementedError()

    def get_path(self) -> Path:
        raise NotImplementedError()

    def get_raw_text(self, content: str | ET.Element) -> str:
        raise NotImplementedError()

    def get_img_bytestr(self, image_id: str) -> tuple[str, bytes]:
        raise NotImplementedError()

    def cleanup(self) -> None:
        shutil.rmtree(self.get_tempdir())

    # TODO: maybe cache @lru_cache
    def get_toc(self) -> tuple[TocEntry, ...]:
        raise NotImplementedError()

    def iter_parsed_contents(self) -> Iterator[Segment]:
        raise NotImplementedError()

    def get_meta(self) -> BookMetadata:
        raise NotImplementedError("Ebook.get_meta() not implemented")
