import sys

from .app import Baca
from .utils.cli import find_file


def main():
    ebook_path = find_file()
    return sys.exit(Baca(ebook_path).run())


if __name__ == "__main__":
    main()
