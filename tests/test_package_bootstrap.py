from __future__ import annotations

import pytest

import mstr_qualify
from mstr_qualify.__main__ import build_parser, main


def test_package_exposes_version() -> None:
    assert mstr_qualify.__version__ == "0.0.0"


def test_parser_uses_expected_program_name() -> None:
    assert build_parser().prog == "mstr-qualify"


def test_no_argument_bootstrap_is_offline_safe(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "MSTR preconstruction qualification harness" in captured.out


def test_unimplemented_command_fails_closed() -> None:
    # T010 implements validate/rights/candidate static/manifest validate.
    # Later-task command families (e.g. measurement) must still fail closed.
    with pytest.raises(SystemExit) as excinfo:
        main(["measure"])
    assert excinfo.value.code == 2


def test_help_mentions_offline_command_families(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    for family in ("validate", "rights", "candidate", "manifest"):
        assert family in captured.out
