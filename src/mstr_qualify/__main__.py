"""Executable entry point for the MSTR qualification CLI (T010 onward).

The real offline qualification commands live in :mod:`mstr_qualify.cli`.
`build_parser` and `main` are re-exported here so the console-script entry
point (`mstr-qualify = mstr_qualify.__main__:main`) and existing imports
keep working.
"""

from __future__ import annotations

from .cli import build_parser, main

__all__ = ["build_parser", "main"]

if __name__ == "__main__":
    raise SystemExit(main())
