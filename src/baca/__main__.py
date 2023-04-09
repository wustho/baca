import sys

from rich.console import Console
from rich.text import Text

from baca.app import Baca
from baca.db import migrate
from baca.exceptions import EbookNotFound, FormatNotSupported
from baca.utils.cli import find_file, get_ebook_class


def main():
    try:
        migrate()
        ebook_path = find_file()
        ebook_class = get_ebook_class(ebook_path)
        return sys.exit(Baca(ebook_path=ebook_path, ebook_class=ebook_class).run())

    except (Exception, EbookNotFound, FormatNotSupported) as e:
        console = Console()
        if isinstance(e, (EbookNotFound, FormatNotSupported)):
            console.print(Text(str(e), style="bold red"))
        else:
            console.print_exception()
        sys.exit(-1)


if __name__ == "__main__":
    main()
