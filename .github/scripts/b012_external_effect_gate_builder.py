from __future__ import annotations

import json
import re
from pathlib import Path

AUTHORITY_ID = "B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION"


def main() -> None:
    config_path = Path("configs/task-gate/mstr-000b.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    b012 = config["tasks"]["B012"]
    assert b012["canonical_state"] == "PENDING"
    assert "external_effect_class" not in b012
    assert "required_authority_id" not in b012
    assert config["tasks"]["B011"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert config["tasks"]["B013"]["canonical_state"] == "BLOCKED"
    b012["external_effect_class"] = "MODEL_WEIGHT_ACCESS"
    b012["required_authority_id"] = AUTHORITY_ID
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tasks_path = Path("specs/002-code-model-supremacy-foundation/tasks.md")
    tasks = tasks_path.read_text(encoding="utf-8")
    old = (
        "  Prerequisites: B002 `COMPLETE_CANONICAL`, exact-main `eligible=true`, B010 canonical, "
        "and B011 complete or `NOT_REQUIRED_NO_NEW_ACCESS`. A candidate that needs no new acquisition "
        "but has already-authorized/already-available artifacts MUST still receive equivalent qualification. "
        "B012 may close `NOT_REQUIRED_NO_NEW_CANDIDATES` only when B010 explicitly records "
        "`qualification_candidates=[]` / `NO_NEW_CANDIDATES_REQUIRING_QUALIFICATION`. Reuse canonical "
        "T029-T034 protocols where compatible; if superseded, record migration.  "
    )
    new = (
        "  Prerequisites: B002 `COMPLETE_CANONICAL`, exact-main `eligible=true`, B010 canonical, "
        "and B011 complete or `NOT_REQUIRED_NO_NEW_ACCESS`. Before any B012 action that re-acquires model "
        "weights or executes conversion, quantization, runtime, or model workloads, require canonical "
        f"`{AUTHORITY_ID}`; B011 authority never transfers. A candidate that needs no new acquisition "
        "but has already-authorized/already-available artifacts MUST still receive equivalent qualification. "
        "B012 may close `NOT_REQUIRED_NO_NEW_CANDIDATES` only when B010 explicitly records "
        "`qualification_candidates=[]` / `NO_NEW_CANDIDATES_REQUIRING_QUALIFICATION`. Reuse canonical "
        "T029-T034 protocols where compatible; if superseded, record migration."
    )
    assert old in tasks
    tasks_path.write_text(tasks.replace(old, new, 1), encoding="utf-8")

    contract_path = Path("tests/contract/test_task_gate.py")
    contract = contract_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'def test_b012_is_eligible_after_b011_canonical_closeout\(\) -> None:\n'
        r'.*?\n\n'
        r'def test_b006_fails_closed_when_b005_discovery_manifest_is_missing',
        re.S,
    )
    replacement = "\n".join(
        [
            "def test_b012_fails_closed_without_exact_equivalent_qualification_authority() -> None:",
            "    result = evaluate_task_snapshot(\"B012\", canonical_main=_CANONICAL_MAIN)",
            "",
            "    assert result[\"eligible\"] is False",
            "    assert result[\"state_consistency_result\"][\"observed_state\"] == \"PENDING\"",
            "    predecessor = next(row for row in result[\"prerequisite_results\"] if row[\"task_id\"] == \"B011\")",
            "    assert predecessor[\"satisfied\"] is True",
            "    assert result[\"authority_result\"] == {",
            "        \"required\": True,",
            f"        \"authority_id\": \"{AUTHORITY_ID}\",",
            "        \"satisfied\": False,",
            "        \"reasons\": [\"authority.canonical_envelope_missing_or_invalid\"],",
            "    }",
            "    assert \"authority.canonical_envelope_missing_or_invalid\" in result[\"reasons\"]",
            "    assert \"task.blocked\" not in result[\"reasons\"]",
            "    assert \"task.unresolved_binding\" not in result[\"reasons\"]",
            "    validate_instance(\"mstr-task-eligibility-v0\", result)",
            "",
            "",
            "def test_b006_fails_closed_when_b005_discovery_manifest_is_missing",
        ]
    )
    contract, count = pattern.subn(replacement, contract, count=1)
    assert count == 1
    contract_path.write_text(contract, encoding="utf-8")

    cli_path = Path("tests/integration/test_task_gate_cli.py")
    cli = cli_path.read_text(encoding="utf-8")
    cli_pattern = re.compile(
        r'def test_task_eligible_b012_successor_returns_zero\(.*?\n\n'
        r'def test_task_eligible_configuration_error_returns_two',
        re.S,
    )
    cli_replacement = "\n".join(
        [
            "def test_task_eligible_b012_missing_authority_returns_one(",
            "    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]",
            ") -> None:",
            "    expected = evaluate_task_snapshot(\"B012\", canonical_main=_CANONICAL_MAIN)",
            "",
            "    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:",
            "        assert task_id == \"B012\"",
            "        return expected",
            "",
            "    monkeypatch.setattr(",
            "        \"mstr_qualify.cli.evaluate_task_eligibility\", fake_evaluate_task_eligibility",
            "    )",
            "    exit_code = main([\"task\", \"eligible\", \"B012\"])",
            "    payload = _stdout_json(capsys)",
            "    assert exit_code == 1",
            "    assert payload == expected",
            "    assert payload[\"eligible\"] is False",
            "    assert payload[\"authority_result\"][\"required\"] is True",
            "    assert payload[\"authority_result\"][\"satisfied\"] is False",
            "    assert payload[\"authority_result\"][\"authority_id\"] == (",
            f"        \"{AUTHORITY_ID}\"",
            "    )",
            "    assert \"authority.canonical_envelope_missing_or_invalid\" in payload[\"reasons\"]",
            "    validate_instance(\"mstr-task-eligibility-v0\", payload)",
            "",
            "",
            "def test_task_eligible_configuration_error_returns_two",
        ]
    )
    cli, cli_count = cli_pattern.subn(cli_replacement, cli, count=1)
    assert cli_count == 1
    cli_path.write_text(cli, encoding="utf-8")

    convergence_path = Path("tests/contract/test_convergence_external_bindings.py")
    convergence = convergence_path.read_text(encoding="utf-8")
    marker = '    assert tasks["B012"]["canonical_state"] == "PENDING"\n'
    assert convergence.count(marker) == 1
    replacement = (
        marker
        + '    assert tasks["B012"]["external_effect_class"] == "MODEL_WEIGHT_ACCESS"\n'
        + '    assert tasks["B012"]["required_authority_id"] == (\n'
        + f'        "{AUTHORITY_ID}"\n'
        + '    )\n'
    )
    convergence_path.write_text(convergence.replace(marker, replacement, 1), encoding="utf-8")


if __name__ == "__main__":
    main()
