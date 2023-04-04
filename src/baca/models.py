from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Literal

from peewee import CharField, DateTimeField, FloatField, IntegerField, Model, SqliteDatabase

from .utils.user_appdirs import retrieve_user_cache_dbfile

db = SqliteDatabase(retrieve_user_cache_dbfile())


class BaseModel(Model):
    class Meta:
        database = db


class DbMetadata(BaseModel):
    version = IntegerField(primary_key=True)
    migrated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "metadata"


class ReadingHistory(BaseModel):
    filepath = CharField(primary_key=True)
    title = CharField(null=True)
    author = CharField(null=True)
    reading_progress = FloatField(null=False)
    last_read = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = "reading_history"


@dataclass(frozen=True)
class Migration:
    version: int
    migrate: Callable[[], None]


class SegmentType(Enum):
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
    search_forward: list[str]
    search_backward: list[str]
    next_match: list[str]
    prev_match: list[str]
    confirm: list[str]
    close: list[str]
    screenshot: list[str]


@dataclass(frozen=True)
class Config:
    preferred_image_viewer: str
    max_text_width: str
    text_justification: Literal["default", "center", "full", "right", "left"]
    pretty: bool
    page_scroll_duration: float
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
    nav_point: str | None


@dataclass(frozen=True)
class KeyMap:
    keys: list[str]
    action: Callable


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int


@dataclass(frozen=True)
class SearchMode:
    pattern_str: str
    current_coord: Coordinate
    forward: bool = True
    saved_position: float = 0.0
