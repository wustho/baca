import dataclasses
import os
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path
from typing import Callable, Iterator
from urllib.parse import unquote, urljoin, urlparse

from ..models import BookMetadata, Segment, TocEntry
from ..utils.html_parser import parse_html_to_segmented_md
from ..utils.tempdir import create_tempdir
from .base import Ebook


class Epub(Ebook):
    NAMESPACE = {
        "DAISY": "http://www.daisy.org/z3986/2005/ncx/",
        "OPF": "http://www.idpf.org/2007/opf",
        "CONT": "urn:oasis:names:tc:opendocument:xmlns:container",
        "XHTML": "http://www.w3.org/1999/xhtml",
        "EPUB": "http://www.idpf.org/2007/ops",
        # Dublin Core
        "DC": "http://purl.org/dc/elements/1.1/",
    }

    def __init__(self, ebook_path: Path):
        self._path = ebook_path.resolve()
        self._file: zipfile.ZipFile = zipfile.ZipFile(ebook_path, "r")
        self._tempdir = create_tempdir()

    @staticmethod
    def _parse_content_opf(
        content_opf: ET.ElementTree, root_dirpath: str, *, path_resolver: Callable = urljoin
    ) -> tuple[str, ...]:
        # cont = ET.parse(self.file.open(self.root_filepath)).getroot()
        manifests: list[tuple[str, str]] = []
        for manifest_elem in content_opf.findall("OPF:manifest/*", Epub.NAMESPACE):
            # EPUB3
            # if manifest_elem.get("id") != "ncx" and manifest_elem.get("properties") != "nav":
            if (
                manifest_elem.get("media-type") != "application/x-dtbncx+xml"
                and manifest_elem.get("properties") != "nav"
            ):
                manifest_id = manifest_elem.get("id")
                manifest_href = manifest_elem.get("href")
                manifests.append((manifest_id, manifest_href))  # type: ignore

        spines: list[str] = []
        contents: list[str] = []
        for spine_elem in content_opf.findall("OPF:spine/*", Epub.NAMESPACE):
            idref = spine_elem.get("idref")
            spines.append(idref)  # type: ignore
        for spine in spines:
            for manifest in manifests:
                if spine == manifest[0]:
                    # book_contents.append(root_dirpath + unquote(manifest[1]))
                    contents.append(unquote(manifest[1]))
                    manifests.remove(manifest)
                    # TODO: test is break necessary
                    break

        return tuple(path_resolver(root_dirpath, content) for content in contents)

    @staticmethod
    def _parse_toc(
        toc: ET.Element, version: str, root_dirpath, *, path_resolver: Callable = urljoin
    ) -> tuple[TocEntry, ...]:
        if version in {"1.0", "2.0"}:
            navPoints = toc.findall("DAISY:navMap//DAISY:navPoint", Epub.NAMESPACE)
        elif version == "3.0":
            navPoints = toc.findall("XHTML:body//XHTML:nav[@EPUB:type='toc']//XHTML:a", Epub.NAMESPACE)
        else:
            raise NotImplementedError(f"Unsupported Epub version: {version}")

        toc_entries: list[TocEntry] = []
        for navPoint in navPoints:
            if version in {"1.0", "2.0"}:
                src_elem = navPoint.find("DAISY:content", Epub.NAMESPACE)
                src = src_elem.get("src")  # type: ignore

                name_elem = navPoint.find("DAISY:navLabel/DAISY:text", Epub.NAMESPACE)
                name = name_elem.text  # type: ignore
            elif version == "3.0":
                src_elem = navPoint
                src = src_elem.get("href")

                name = "".join(list(navPoint.itertext()))
            else:
                raise NotImplementedError(f"Unsupported Epub version: {version}")

            if name is not None:
                toc_entries.append(
                    TocEntry(
                        label=name,
                        # content_index=idx,
                        # section=src_id[1] if len(src_id) == 2 else None,
                        value=path_resolver(root_dirpath, unquote(src)),  # type: ignore
                    )
                )
        return tuple(toc_entries)

    @property
    def _root_filepath(self) -> str:
        container = ET.parse(self._file.open("META-INF/container.xml"))
        rootfile_elem = container.find("CONT:rootfiles/CONT:rootfile", Epub.NAMESPACE)
        return rootfile_elem.attrib["full-path"]  # type: ignore

    @property
    def _root_dirpath(self) -> str:
        dirname = os.path.dirname(self._root_filepath)
        return f"{dirname}/" if dirname != "" else ""

    @property
    def _content_opf(self) -> ET.ElementTree:
        return ET.parse(self._file.open(self._root_filepath))

    @property
    def _relactive_toc_ncx_path(self) -> str:
        if self._version in {"1.0", "2.0"}:
            # "OPF:manifest/*[@id='ncx']"
            relative_toc = self._content_opf.find(
                "OPF:manifest/*[@media-type='application/x-dtbncx+xml']", Epub.NAMESPACE
            )
        elif self._version == "3.0":
            relative_toc = self._content_opf.find("OPF:manifest/*[@properties='nav']", Epub.NAMESPACE)
        else:
            raise NotImplementedError(f"Unsupported Epub version: {self._version}")

        return relative_toc.get("href")  # type: ignore

    @property
    def _toc_ncx(self) -> ET.Element:
        toc_ncx_path = urljoin(self._root_dirpath, self._relactive_toc_ncx_path)  # type: ignore
        return ET.parse(self._file.open(toc_ncx_path)).getroot()

    @property
    def _version(self) -> str:
        return self._content_opf.getroot().get("version")  # type: ignore

    def _get_contents(self) -> tuple[str, ...] | tuple[ET.Element, ...]:
        return Epub._parse_content_opf(self._content_opf, self._root_dirpath)

    def get_path(self) -> Path:
        return self._path

    def get_tempdir(self) -> Path:
        return self._tempdir

    def get_meta(self) -> BookMetadata:
        metadata: dict[str, str | None] = {}
        for field in dataclasses.fields(BookMetadata):
            element = self._content_opf.find(f".//DC:{field.name}", Epub.NAMESPACE)
            if element is not None:
                metadata[field.name] = element.text
        return BookMetadata(**metadata)

    def get_toc(self) -> tuple[TocEntry, ...]:
        return Epub._parse_toc(self._toc_ncx, self._version, self._root_dirpath)

    def get_raw_text(self, content_path: str | ET.Element) -> str:
        assert isinstance(content_path, str)

        max_tries: int | None = None

        # use try-except block to catch
        # zlib.error: Error -3 while decompressing data: invalid distance too far back
        # seems like caused by multiprocessing
        tries = 0
        while True:
            try:
                content = self._file.open(content_path).read()
                break
            except zlib.error as e:
                tries += 1
                if max_tries is not None and tries >= max_tries:
                    raise e

        return content.decode("utf-8")

    def get_img_bytestr(self, impath: str) -> tuple[str, bytes]:
        assert isinstance(self._file, zipfile.ZipFile)
        return os.path.basename(impath), self._file.read(impath)

    def iter_parsed_contents(self) -> Iterator[Segment]:
        toc_entries = self.get_toc()
        for content in self._get_contents():
            ids_for_this_content = [
                urlparse(t.value).fragment
                for t in toc_entries
                if t.value.startswith(content) and urlparse(t.value).fragment != ""
            ]
            raw = self.get_raw_text(content)
            for segment in parse_html_to_segmented_md(raw, str(content), ids_to_find=ids_for_this_content):
                yield segment
