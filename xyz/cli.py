"""Command-line entry point for XYZ Code Intelligence."""

import argparse
import sys

from xyz import __version__


def _parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(prog="xyz")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", metavar="{ingest,query,eval}")
    for command in ("ingest", "query", "eval"):
        subparsers.add_parser(command, help="not implemented until gh11-p4")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and return a process exit status."""
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if args.command is None:
        parser.print_help()
        return 0

    parser.print_usage(file=sys.stderr)
    print(f"xyz: error: {args.command} not implemented until gh11-p4", file=sys.stderr)
    return 2
