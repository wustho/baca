from pathlib import Path
from typing import Iterator

from ..models import ReadingHistory


def get_all_reading_history() -> Iterator[ReadingHistory]:
    for rh in ReadingHistory.select().order_by(ReadingHistory.last_read.desc()):  # type: ignore
        if Path(rh.filepath).is_file():
            yield rh
        else:
            rh.delete_instance()


def get_latest_read_ebook() -> Path | None:
    try:
        last_read_ebook = ReadingHistory.select().order_by(ReadingHistory.last_read.desc()).get()  # type: ignore
        last_read_ebook = Path(last_read_ebook.filepath)
        return last_read_ebook if last_read_ebook.is_file() else None
    except ReadingHistory.DoesNotExist:
        return None
