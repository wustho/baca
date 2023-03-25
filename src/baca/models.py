from dataclasses import dataclass
from enum import Enum
from typing import Callable


@dataclass(frozen=True)
class BookMetadata:
    title: str | None = None
    creator: str | None = None
    description: str | None = None
    publisher: str | None = None
    date: str | None = None
    language: str | None = None
    format: str | None = None
    identifier: str | None = None
    source: str | None = None


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


@dataclass
class KeyMap:
    keys: list[str]
    action: Callable
