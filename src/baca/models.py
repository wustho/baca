from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class TocEntry:
    label: str
    value: str


class SegmentType(Enum):
    SECTION = "section"
    IMAGE = "image"
    BODY = "body"


class Layers(Enum):
    CONTENT = "content"
    WINDOWS = "windows"


@dataclass(frozen=True)
class Segment:
    type: SegmentType
    content: str
