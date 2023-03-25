import argparse
import textwrap

from .. import __appname__, __version__


def parse_cli_args() -> argparse.Namespace:
    prog = __appname__
    positional_arg_help_str = "[PATH | # | PATTERN | URL]"
    args_parser = argparse.ArgumentParser(
        prog=prog,
        # usage=f"%(prog)s [-h] [-r] [-d] [-v] {positional_arg_help_str}",
        usage=f"%(prog)s [-h] [-v] {positional_arg_help_str}",
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
    # TODO:
    # args_parser.add_argument("-r", "--history", action="store_true", help="print reading history")
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
        help="ebook path, history number, pattern or URL",
    )
    return args_parser.parse_args()
