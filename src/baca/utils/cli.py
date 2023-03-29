import argparse
import sys
import textwrap
from pathlib import Path
from typing import Type

from rich.console import Console
from rich.table import Table

from .. import __appname__, __version__
from ..ebooks import Azw, Ebook, Epub, Mobi
from ..exceptions import EbookNotFound, FormatNotSupported
from .queries import (
    get_all_reading_history,
    get_best_match_from_history,
    get_last_read_ebook,
    get_nth_file_from_history,
)


def format_file_size(pathstr: str) -> str:
    byte_size = Path(pathstr).stat().st_size
    return f"{round(byte_size / 1024, 2)} kb" if byte_size <= 1024**2 else f"{round(byte_size / (1024 ** 2), 2)} mb"


def print_reading_history() -> None:
    table = Table(title="Baca History")
    table.add_column("#", style="cyan", no_wrap=False, justify="right")
    table.add_column("Last Read", style="cyan", no_wrap=False)
    table.add_column("Progress", style="cyan", no_wrap=False, justify="right")
    table.add_column("Title", style="magenta", no_wrap=False)
    table.add_column("Author", style="green", no_wrap=False)
    table.add_column("Path", style="white", no_wrap=False)
    table.add_column("Size", style="blue", no_wrap=False, justify="right")

    for n, rh in enumerate(get_all_reading_history()):
        table.add_row(
            str(n + 1),
            f"{rh.last_read:%I:%M %p %b %d, %Y}",
            f"{round(rh.reading_progress*100, 2)}%",  # type: ignore
            rh.title,  # type: ignore
            rh.author,  # type: ignore
            rh.filepath,  # type: ignore
            format_file_size(rh.filepath),  # type: ignore
        )

    Console().print(table)


def parse_cli_args() -> argparse.Namespace:
    prog = __appname__
    positional_arg_help_str = "[PATH | # | PATTERN ]"
    args_parser = argparse.ArgumentParser(
        prog=prog,
        usage=f"%(prog)s [-h] [-r] [-v] {positional_arg_help_str}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="TUI Ebook Reader",
        epilog=textwrap.dedent(
            f"""\
        examples:
          {prog} /path/to/ebook    read /path/to/ebook file
          {prog} 3                 read #3 file from reading history
          {prog} count monte       read file matching 'count monte'
                                 from reading history
        """
        ),
    )
    args_parser.add_argument("-r", "--history", action="store_true", help="print reading history")
    args_parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"v{__version__}",
        help="print version and exit",
    )
    args_parser.add_argument(
        "ebook",
        action="store",
        nargs="*",
        metavar=positional_arg_help_str,
        help="ebook path, history number or pattern",
    )
    return args_parser.parse_args()


def find_file() -> Path:
    args = parse_cli_args()
    if args.history:
        print_reading_history()
        sys.exit(0)

    elif len(args.ebook) == 0:
        last_read = get_last_read_ebook()
        if last_read is not None:
            return last_read
        else:
            raise EbookNotFound("found no last read ebook file!")

    elif len(args.ebook) == 1:
        arg = args.ebook[0]
        try:
            nth = int(arg)
            ebook_path = get_nth_file_from_history(nth)
            if ebook_path is None:
                print_reading_history()
                raise EbookNotFound(f"#{nth} file not found from history!")

            else:
                return ebook_path

        except ValueError:
            if Path(arg).is_file():
                return Path(arg)

    pattern = " ".join(args.ebook)
    ebook_path = get_best_match_from_history(pattern)
    if ebook_path is None:
        print_reading_history()
        raise EbookNotFound("found no matching ebook from history!")
    else:
        return ebook_path


def get_ebook_class(ebook_path: Path) -> Type[Ebook]:
    ext = ebook_path.suffix.lower()
    try:
        return {
            ".epub": Epub,
            ".epub3": Epub,
            ".azw": Azw,
            ".azw3": Azw,
            ".mobi": Mobi,
        }[ext]
    except KeyError:
        raise FormatNotSupported("format not supported!")
