from typing import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter as _MarkdownConverter

from ..models import Segment, SegmentType


class MarkdownConverter(_MarkdownConverter):
    def convert_img(self, el, text, convert_as_inline):
        return ""


def split_html_to_segments(
    html_src: str, section_name: str, *, ids_to_find: list[str] | None = None
) -> Iterator[Segment]:
    """
    :param ids_to_find:
        ids_to_find is url fragment (eg. https://url.com/content.html#fragment) to find inside given `html_src`

        - if None will find all possible id(s)
        - if [] then, will skip finding id(s) section in html_src
    """
    soup = BeautifulSoup(html_src, "html.parser", store_line_numbers=True)
    body = soup.find("body")
    body_html = str(body).replace("\n", " ")
    body = BeautifulSoup(body_html, "html.parser")

    find_nav_points = ids_to_find is None or len(ids_to_find) > 0
    if find_nav_points:
        section_elems = body.find_all(id=True if ids_to_find is None else ids_to_find)
    else:
        section_elems = []
    img_elems = body.find_all(["img", "image"])
    all_elems = sorted(section_elems + img_elems, key=lambda x: [x.sourceline, x.sourcepos])  # type: ignore

    start = 0
    nav_point = section_name
    for elem in all_elems:
        yield Segment(type=SegmentType.BODY, content=body_html[start : elem.sourcepos], nav_point=nav_point)  # type: ignore

        start = elem.sourcepos
        fragment = elem.get("id")
        nav_point = f"{section_name}#{fragment}" if find_nav_points and fragment is not None else None

        if elem.name in {"img", "image"}:  # type: ignore
            img_src = elem.get("src") or elem.get("href")  # type: ignore
            if img_src is not None:
                # NOTE: urljoin should be able to handle relative path. ie urljoin("a", "b") == "b"
                yield Segment(type=SegmentType.IMAGE, content=urljoin(section_name, img_src), nav_point=nav_point)

    yield Segment(type=SegmentType.BODY, content=body_html[start:], nav_point=nav_point)


def parse_html_to_segmented_md(
    html_src: str, section_name: str, *, ids_to_find: list[str] | None = None
) -> Iterator[Segment]:
    for segment in split_html_to_segments(html_src, section_name, ids_to_find=ids_to_find):
        yield Segment(
            type=segment.type,
            content=MarkdownConverter().convert(segment.content)
            if segment.type == SegmentType.BODY
            else segment.content,
            nav_point=segment.nav_point,
        )
