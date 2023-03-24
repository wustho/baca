from baca.app import Baca
from baca.ebooks import Epub


class Debug(Baca):
    def __init__(self):
        file = "tmp/alice.epub"
        ebook = Epub(file)
        super().__init__(ebook)
