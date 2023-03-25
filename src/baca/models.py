from dataclasses import dataclass
from enum import Enum
from typing import Callable, Literal


class SegmentType(Enum):
    SECTION = "section"
    IMAGE = "image"
    BODY = "body"


@dataclass(frozen=True)
class Color:
    bg: str
    fg: str
    accent: str


@dataclass(frozen=True)
class Keymaps:
    toggle_dark: list[str]
    scroll_down: list[str]
    scroll_up: list[str]
    home: list[str]
    end: list[str]
    page_up: list[str]
    page_down: list[str]
    open_toc: list[str]
    open_metadata: list[str]
    open_help: list[str]
    close: list[str]
    screenshot: list[str]


@dataclass(frozen=True)
class Config:
    max_text_width: str
    text_justification: Literal["default", "center", "full", "right", "left"]
    pretty: bool
    dark: Color
    light: Color
    keymaps: Keymaps


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


@dataclass(frozen=True)
class Segment:
    type: SegmentType
    content: str


@dataclass(frozen=True)
class KeyMap:
    keys: list[str]
    action: Callable
