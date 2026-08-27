from __future__ import annotations

import json
from typing import Any

import pytest

from mstr_qualify.__main__ import main
from mstr_qualify.errors import QualificationError
from mstr_qualify.schemas import validate_instance
from mstr_qualify.task_gate import evaluate_task_snapshot

_CANONICAL_MAIN = "a" * 40


def _stdout_json(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    captured = capsys.readouterr()
    assert captured.err == ""
    decoded = json.loads(captured.out)
    assert isinstance(decoded, dict)
    return decoded


def test_task_eligible_b002_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = evaluate_task_snapshot("B002", canonical_main=_CANONICAL_MAIN)
    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility",
        lambda task_id: expected,
    )

    exit_code = main(["task", "eligible", "B002"])
    payload = _stdout_json(capsys)

    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b003_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = evaluate_task_snapshot("B003", canonical_main=_CANONICAL_MAIN)
    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility",
        lambda task_id: expected,
    )

    exit_code = main(["task", "eligible", "B003"])
    payload = _stdout_json(capsys)

    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b004_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = evaluate_task_snapshot("B004", canonical_main=_CANONICAL_MAIN)
    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility",
        lambda task_id: expected,
    )

    exit_code = main(["task", "eligible", "B004"])
    payload = _stdout_json(capsys)

    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b006_successor_returns_zero(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = evaluate_task_snapshot("B006", canonical_main=_CANONICAL_MAIN)
    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility",
        lambda task_id: expected,
    )

    exit_code = main(["task", "eligible", "B006"])
    payload = _stdout_json(capsys)

    assert exit_code == 0
    assert payload == expected
    assert payload["eligible"] is True
    assert payload["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_configuration_error_returns_two(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_closed(task_id: str) -> dict[str, Any]:
        raise QualificationError(
            "unknown task id",
            code="task_gate.task_unknown",
            details={"task_id": task_id},
        )

    monkeypatch.setattr("mstr_qualify.cli.evaluate_task_eligibility", fail_closed)

    exit_code = main(["task", "eligible", "B999"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    payload = json.loads(captured.err)
    assert payload["status"] == "error"
    assert payload["command"] == "task"
    assert payload["code"] == "task_gate.task_unknown"


def test_task_eligible_parser_exposes_no_mutation_surface() -> None:
    from mstr_qualify.cli import build_parser

    parser = build_parser()
    args = parser.parse_args(["task", "eligible", "B003"])

    assert args.command == "task"
    assert args.task_command == "eligible"
    assert args.task_id == "B003"
    assert not hasattr(args, "canonical_main")

def test_task_eligible_parser_rejects_caller_supplied_main() -> None:
    from mstr_qualify.cli import build_parser

    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["task", "eligible", "B003", "--canonical-main", "a" * 40])
