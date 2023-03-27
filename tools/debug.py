from pathlib import Path

from baca.app import Baca
from baca.utils.cli import get_ebook_class


class Debug(Baca):
    def __init__(self):
        # file = Path("tmp/alice.azw3")
        file = Path("tmp/frankenstein.older.mobi")
        # file = Path("tmp/frankenstein.mobi")
        super().__init__(file, get_ebook_class(file))
