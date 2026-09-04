from __future__ import annotations

from pathlib import Path

CONTRACT_PATH = Path.cwd() / "tests/contract/test_task_gate.py"
CLI_PATH = Path.cwd() / "tests/integration/test_task_gate_cli.py"


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = CONTRACT_PATH.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '''def test_explicitly_blocked_task_never_becomes_eligible() -> None:\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is False\n    assert "task.blocked" in result["reasons"]\n    assert "task.unresolved_binding" in result["reasons"]\n''',
        '''def test_exact_founder_authority_unblocks_pending_b011() -> None:\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is True\n    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n    assert "task.blocked" not in result["reasons"]\n    assert "task.unresolved_binding" not in result["reasons"]\n    assert result["authority_result"]["authority_id"] == (\n        "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"\n    )\n    assert result["authority_result"]["satisfied"] is True\n''',
        label="historical B011 blocked regression",
    )

    text = replace_once(
        text,
        '''def test_b011_stays_weight_access_fail_closed_until_b010_resolution() -> None:\n    catalog = load_task_catalog()\n    node = catalog.nodes["B011"]\n    assert node["canonical_state"] == "BLOCKED"\n    assert node["external_effect_class"] == "MODEL_WEIGHT_ACCESS"\n    assert node["required_authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n    assert result["eligible"] is False\n    assert result["authority_result"]["required"] is True\n    assert result["authority_result"]["satisfied"] is False\n''',
        '''def test_b011_weight_access_observes_exact_authority_after_b010_resolution() -> None:\n    catalog = load_task_catalog()\n    node = catalog.nodes["B011"]\n    assert node["canonical_state"] == "PENDING"\n    assert node["external_effect_class"] == "MODEL_WEIGHT_ACCESS"\n    assert node["required_authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n    assert result["eligible"] is True\n    assert result["authority_result"]["required"] is True\n    assert result["authority_result"]["satisfied"] is True\n''',
        label="B011 fail-closed-until-resolution regression",
    )

    text = replace_once(
        text,
        '''def test_b014_closeout_does_not_authorize_b011_weight_access() -> None:\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is False\n    assert result["state_consistency_result"]["observed_state"] == "BLOCKED"\n    assert result["authority_result"]["required"] is True\n    assert result["authority_result"]["satisfied"] is False\n    assert result["authority_result"]["authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"\n    validate_instance("mstr-task-eligibility-v0", result)\n''',
        '''def test_b014_closeout_does_not_change_b011_exact_authority_identity() -> None:\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is True\n    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n    assert result["authority_result"]["required"] is True\n    assert result["authority_result"]["satisfied"] is True\n    assert result["authority_result"]["authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"\n    validate_instance("mstr-task-eligibility-v0", result)\n''',
        label="B014/B011 authority isolation regression",
    )

    CONTRACT_PATH.write_text(text, encoding="utf-8")

    cli = CLI_PATH.read_text(encoding="utf-8")
    cli = replace_once(
        cli,
        '''def test_task_eligible_b011_blocked_returns_one(\n    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]\n) -> None:\n    expected = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:\n        assert task_id == "B011"\n        return expected\n\n    monkeypatch.setattr(\n        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility\n    )\n    exit_code = main(["task", "eligible", "B011"])\n    payload = _stdout_json(capsys)\n    assert exit_code == 1\n    assert payload == expected\n    assert payload["eligible"] is False\n    assert "task.blocked" in payload["reasons"]\n    validate_instance("mstr-task-eligibility-v0", payload)\n''',
        '''def test_task_eligible_b011_authorized_returns_zero(\n    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]\n) -> None:\n    expected = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:\n        assert task_id == "B011"\n        return expected\n\n    monkeypatch.setattr(\n        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility\n    )\n    exit_code = main(["task", "eligible", "B011"])\n    payload = _stdout_json(capsys)\n    assert exit_code == 0\n    assert payload == expected\n    assert payload["eligible"] is True\n    assert payload["authority_result"]["satisfied"] is True\n    validate_instance("mstr-task-eligibility-v0", payload)\n''',
        label="B011 CLI blocked regression",
    )
    CLI_PATH.write_text(cli, encoding="utf-8")


if __name__ == "__main__":
    main()
