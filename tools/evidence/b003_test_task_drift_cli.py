from __future__ import annotations

import json

import pytest

from mstr_qualify.cli import main


def _stdout_json(capsys: pytest.CaptureFixture[str]) -> dict[str, object]:
    output = capsys.readouterr().out
    parsed = json.loads(output)
    assert isinstance(parsed, dict)
    return parsed


def test_task_drift_clean_returns_zero(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report = {
        "status": "clean",
        "canonical_main": "a" * 40,
        "tasks_checked": 34,
        "findings": [],
    }
    monkeypatch.setattr("mstr_qualify.cli.detect_canonical_drift", lambda: report)

    exit_code = main(["task", "drift"])
    payload = _stdout_json(capsys)

    assert exit_code == 0
    assert payload == report


def test_task_drift_findings_return_one(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report = {
        "status": "drift",
        "canonical_main": "b" * 40,
        "tasks_checked": 34,
        "findings": [
            {
                "task_id": "B003",
                "code": "implementation.merged_while_active",
                "details": {"pr_number": 50},
            }
        ],
    }
    monkeypatch.setattr("mstr_qualify.cli.detect_canonical_drift", lambda: report)

    exit_code = main(["task", "drift"])
    payload = _stdout_json(capsys)

    assert exit_code == 1
    assert payload == report
