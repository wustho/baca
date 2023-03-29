import warnings
from pathlib import Path
from typing import Iterator

from ..models import ReadingHistory

MIN_FUZZY_MATCH_RATIO = 10


def get_all_reading_history() -> Iterator[ReadingHistory]:
    for rh in ReadingHistory.select().order_by(ReadingHistory.last_read.desc()):  # type: ignore
        if Path(rh.filepath).is_file():
            yield rh
        else:
            rh.delete_instance()


def get_best_match_from_history(pattern: str) -> Path | None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fuzzywuzzy import fuzz

    match_ratios = [
        (rh.filepath, fuzz.ratio(tomatch, pattern))
        for rh in get_all_reading_history()
        for tomatch in [rh.filepath, f"{rh.title} {rh.author}"]
    ]
    matches = [(Path(path), ratio) for path, ratio in match_ratios if ratio > MIN_FUZZY_MATCH_RATIO]  # type: ignore
    return None if len(matches) == 0 else sorted(matches, key=lambda x: -x[1])[0][0]


def get_nth_file_from_history(nth: int) -> Path | None:
    try:
        return Path(list(get_all_reading_history())[nth - 1].filepath)  # type: ignore
    except IndexError:
        return None


def get_last_read_ebook() -> Path | None:
    try:
        last_read_ebook = ReadingHistory.select().order_by(ReadingHistory.last_read.desc()).get()  # type: ignore
        last_read_ebook = Path(last_read_ebook.filepath)
        return last_read_ebook if last_read_ebook.is_file() else None
    except ReadingHistory.DoesNotExist:
        return None
