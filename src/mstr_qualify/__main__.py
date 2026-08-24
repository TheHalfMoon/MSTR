"""Minimal package entry point for the T003 bootstrap.

The real qualification CLI is implemented by later canonical tasks. T003 only
proves that the package has a stable executable entry point and fails closed for
commands that have not yet been implemented.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mstr-qualify",
        description="MSTR preconstruction qualification harness",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "command",
        nargs="?",
        help="Qualification command family. Implemented by later MSTR-000 tasks.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    parser.error(
        f"command {args.command!r} is not implemented in T003; "
        "later canonical tasks add qualification commands"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
