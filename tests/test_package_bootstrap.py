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
    with pytest.raises(SystemExit) as excinfo:
        main(["validate"])
    assert excinfo.value.code == 2
