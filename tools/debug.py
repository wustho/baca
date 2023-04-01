from pathlib import Path

from baca.app import Baca
from baca.utils.cli import get_ebook_class
from baca.utils.queries import get_last_read_ebook


class Debug(Baca):
    def __init__(self):
        # file = Path("tmp/alice.azw3")
        file = get_last_read_ebook()
        assert file is not None
        # file = Path("tmp/andy.epub")
        # file = Path("tmp/frankenstein.older.mobi")
        # file = Path("tmp/frankenstein.mobi")
        super().__init__(file, get_ebook_class(file))
