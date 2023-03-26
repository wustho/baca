from baca.app import Baca
from pathlib import Path
from baca.ebooks import Epub


class Debug(Baca):
    def __init__(self):
        file = Path("tmp/alice.epub")
        super().__init__(file)
