import os
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .app import Baca
from .ebooks import Epub
from .utils.cli import parse_cli_args
from .utils.queries import get_all_reading_history


def main():
    args = parse_cli_args()
    if args.history:
        table = Table(title="Baca History")
        table.add_column("Last Read", style="cyan", no_wrap=True)
        table.add_column("Progress", style="cyan", no_wrap=True, justify="right")
        table.add_column("Title", style="magenta", no_wrap=True)
        table.add_column("Author", style="green", no_wrap=True)
        table.add_column("Path", style="white", no_wrap=True)

        for rh in get_all_reading_history():
            table.add_row(f"{rh.last_read:%b %d, %Y %I:%M %p}", f"{round(rh.reading_progress*100, 2)}%", rh.title, rh.author, rh.filepath)  # type: ignore

        console = Console()
        console.print(table)
        sys.exit(0)

    if len(args.ebook) and os.path.isfile(args.ebook[0]):
        ebook_path = Path(args.ebook[0])
        return sys.exit(Baca(ebook_path).run())
    # file = "/home/ss/Projects/baca.draft/tmp/pg11-images.epub"
    # file = "/home/ss/Projects/baca.draft/tmp/andyweir.epub"
    # ebook = Epub(file)
    # for s in ebook.iter_parsed_contents():
    #     print(s)
    #     print("==========")
    # print(ebook.get_parsed_contents())
    # print(list(ebook.iter_parsed_contents()))
    # for c in ebook.iter_parsed_contents():
    #     if c.type.value == "section":
    #         print(c)
    # list(ebook.iter_parsed_contents())[0]
    # print(ebook.get_toc())
    # Baca(ebook).run()


if __name__ == "__main__":
    main()
