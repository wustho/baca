import sys

from rich.console import Console

from .app import Baca
from .db import migrate
from .utils.cli import find_file, get_ebook_class


def main():
    try:
        migrate()
        ebook_path = find_file()
        ebook_class = get_ebook_class(ebook_path)
        return sys.exit(Baca(ebook_path=ebook_path, ebook_class=ebook_class).run())
    except Exception:
        Console().print_exception()
        sys.exit(-1)


if __name__ == "__main__":
    main()
