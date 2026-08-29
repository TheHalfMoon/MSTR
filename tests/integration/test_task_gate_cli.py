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


def test_task_eligible_b006_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = evaluate_task_snapshot("B006", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B006"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility",
        fake_evaluate_task_eligibility,
    )

    exit_code = main(["task", "eligible", "B006"])
    payload = _stdout_json(capsys)

    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b007_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B007", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B007"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B007"])
    payload = _stdout_json(capsys)
    assert exit_code == 1 and payload == expected and payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b008_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B008", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B008"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B008"])
    payload = _stdout_json(capsys)
    assert exit_code == 1 and payload == expected and payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b009_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B009", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B009"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B009"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b010_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B010", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B010"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B010"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b011_blocked_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B011"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B011"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.blocked" in payload["reasons"]
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


def test_task_eligible_b014_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B014", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B014"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B014"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b015_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B015", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B015"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B015"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b016_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B016", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B016"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B016"] )
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b017_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B017", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B017"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B017"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b018_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B018", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B018"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B018"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b019_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B019", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B019"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B019"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


def test_task_eligible_b020_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B020", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B020"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B020"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)
