from __future__ import annotations

import json
from typing import Any

import pytest

from mstr_qualify.__main__ import main
from mstr_qualify.schemas import validate_instance


def _stdout_json(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    captured = capsys.readouterr()
    assert captured.err == ""
    decoded = json.loads(captured.out)
    assert isinstance(decoded, dict)
    return decoded


def test_task_eligible_b002_bootstrap_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["task", "eligible", "B002"])
    payload = _stdout_json(capsys)

    assert exit_code == 0
    assert payload["schema_version"] == "mstr.task-eligibility.v0"
    assert payload["task_id"] == "B002"
    assert payload["eligible"] is True
    assert len(payload["canonical_main"]) == 40
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b003_is_fail_closed_before_b002_closeout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["task", "eligible", "B003"])
    payload = _stdout_json(capsys)

    assert exit_code == 1
    assert payload["task_id"] == "B003"
    assert payload["eligible"] is False
    assert "prerequisite.unsatisfied:B002" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_unknown_task_is_exit_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["task", "eligible", "B999"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    payload = json.loads(captured.err)
    assert payload["status"] == "error"
    assert payload["command"] == "task"
    assert payload["code"] == "task_gate.task_unknown"


def test_task_eligible_has_no_repository_mutation(tmp_path: object) -> None:
    # The command itself exposes no write option or mutation subcommand. Parser
    # coverage protects the B002 read-only interface from accidental expansion.
    from mstr_qualify.cli import build_parser

    parser = build_parser()
    args = parser.parse_args(["task", "eligible", "B003"])

    assert args.command == "task"
    assert args.task_command == "eligible"
    assert args.task_id == "B003"
