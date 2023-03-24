import xml.etree.ElementTree as ET
from typing import Iterator

from ..models import BookMetadata, Segment, TocEntry


class Ebook:
    def __init__(self, fileepub: str):
        raise NotImplementedError()

    def get_tempdir(self) -> str:
        raise NotImplementedError()

    def get_path(self) -> str:
        raise NotImplementedError()

    def get_raw_text(self, content: str | ET.Element) -> str:
        raise NotImplementedError()

    def get_img_bytestr(self, image_id: str) -> tuple[str, bytes]:
        raise NotImplementedError()

    def cleanup(self) -> None:
        raise NotImplementedError()

    # TODO: maybe cache @lru_cache
    def get_toc(self) -> tuple[TocEntry, ...]:
        raise NotImplementedError()

    def iter_parsed_contents(self) -> Iterator[Segment]:
        raise NotImplementedError()

    def get_meta(self) -> BookMetadata:
        raise NotImplementedError("Ebook.get_meta() not implemented")
