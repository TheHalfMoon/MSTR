from __future__ import annotations

import json
import re
from pathlib import Path


def main() -> None:
    config_path = Path("configs/task-gate/mstr-000b.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    b011 = config["tasks"]["B011"]
    assert b011["canonical_state"] == "PENDING"
    assert b011["required_authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
    assert config["tasks"]["B012"]["canonical_state"] == "PENDING"
    assert config["tasks"]["B013"]["canonical_state"] == "BLOCKED"
    b011["canonical_state"] = "COMPLETE_CANONICAL"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence_path = Path("evidence/mstr-000b/B011-acquisition.md")
    evidence = evidence_path.read_text(encoding="utf-8")
    old_state = "**Evidence state:** `ACQUISITION_EXECUTED_VERIFIED / CANONICAL_CLOSEOUT_PENDING`  "
    assert old_state in evidence
    evidence = evidence.replace(old_state, "**Evidence state:** `COMPLETE_CANONICAL`", 1)

    founder_marker = (
        "**Founder decision:** "
        "`FOUNDER_B011_MODEL_WEIGHT_ACCESS_DECISION=AUTHORIZE_EXACT_B010_ENVELOPE`\n"
    )
    assert founder_marker in evidence
    provenance = "\n".join(
        [
            "**Closeout entry canonical main:** `a788f55f5251f0be92b33e0765d0436cb321eb8b`",
            "**Implementation PR:** `#157`",
            "**Final implementation head:** `450d9b5b9b3c6aca27222a553dc6230f6eef6783`",
            "**Canonical implementation merge:** `b9aa4f7de8b924d283d09fa8d93dbaceb0f6b4cd`",
            "**Successful acquisition run:** `33865617854`",
            "**Exact-head qualification:** `33867186224`",
            "**Independent substantive semantic review:** `33867564924`",
            "**Mandatory premerge verification:** `33867838434`",
            "**Post-implementation verification:** `33927258696`",
            "**Frontier-planning postmerge verification:** `33926866711`",
        ]
    )
    evidence = evidence.replace(founder_marker, founder_marker + "\n" + provenance + "\n", 1)

    closeout_marker = "## Closeout Boundary\n\n"
    assert closeout_marker in evidence
    prefix = evidence.split(closeout_marker, 1)[0]
    closeout_lines = [
        "## Canonical Closeout",
        "",
        "The B011 acquisition/verification implementation is complete and all required lifecycle evidence is bound above. The earlier fail-closed run `33865467059` remains preserved as negative evidence: no model-weight download started in that attempt.",
        "",
        "This closeout changes only the canonical lifecycle state of B011. It does not re-acquire any model body, does not perform model execution, conversion, quantization, training, large-dataset ingestion, gated-terms acceptance, paid compute/API use, production release, or model-binary persistence.",
        "",
        "The historical authority `B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED` remains an execution record scoped only to B011 and the exact B010 envelope. It does not transfer to, authorize, or widen B012 or any later task. In particular, it does not authorize K2 Horizon or any newly discovered candidate.",
        "",
        "`COMPLETE_CANONICAL` is valid only after this closeout candidate is merged to canonical `main` and the required post-closeout exact-main verification succeeds. Until then, canonical `main` remains authoritative.",
        "",
    ]
    evidence_path.write_text(prefix + "\n".join(closeout_lines), encoding="utf-8")

    tasks_path = Path("specs/002-code-model-supremacy-foundation/tasks.md")
    tasks = tasks_path.read_text(encoding="utf-8")
    old_b011 = (
        "- [ ] **B011 EXPLICIT NEW WEIGHT ACCESS GATE — acquire/verify only "
        "founder-authorized B010 access-required candidates.**"
    )
    new_b011 = old_b011.replace("- [ ]", "- [x]", 1)
    assert old_b011 in tasks
    tasks = tasks.replace(old_b011, new_b011, 1)
    tasks = "\n".join(line.rstrip() for line in tasks.split("\n"))
    boundary = (
        "  Outputs: `artifacts/manifests/B011-acquired-candidates.json` or explicit "
        "no-access decision artifact, runner evidence where executed, "
        "`evidence/mstr-000b/B011-acquisition.md`.\n\n- [ ] **B012"
    )
    assert boundary in tasks
    tasks = tasks.replace(
        boundary,
        (
            "  Outputs: `artifacts/manifests/B011-acquired-candidates.json` or explicit "
            "no-access decision artifact, runner evidence where executed, "
            "`evidence/mstr-000b/B011-acquisition.md`.\n"
            "  Canonical implementation: PR #157 / final head "
            "`450d9b5b9b3c6aca27222a553dc6230f6eef6783` / merge "
            "`b9aa4f7de8b924d283d09fa8d93dbaceb0f6b4cd`.\n\n- [ ] **B012"
        ),
        1,
    )
    tasks_path.write_text(tasks, encoding="utf-8")

    contract_path = Path("tests/contract/test_task_gate.py")
    contract = contract_path.read_text(encoding="utf-8")
    contract_pattern = re.compile(
        r"def test_b011_is_eligible_after_exact_founder_authority_capture\(\) -> None:\n"
        r".*?\n\ndef test_b006_fails_closed_when_b005_discovery_manifest_is_missing",
        re.S,
    )
    contract_replacement = "\n".join(
        [
            "def test_b011_is_terminal_after_canonical_closeout() -> None:",
            "    result = evaluate_task_snapshot(\"B011\", canonical_main=_CANONICAL_MAIN)",
            "",
            "    assert result[\"eligible\"] is False",
            "    assert result[\"state_consistency_result\"][\"observed_state\"] == \"COMPLETE_CANONICAL\"",
            "    assert result[\"state_consistency_result\"][\"satisfied\"] is True",
            "    assert result[\"authority_result\"] == {",
            "        \"required\": True,",
            "        \"authority_id\": \"B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED\",",
            "        \"satisfied\": True,",
            "        \"reasons\": [],",
            "    }",
            "    assert \"task.already_terminal\" in result[\"reasons\"]",
            "    validate_instance(\"mstr-task-eligibility-v0\", result)",
            "",
            "",
            "def test_b012_is_eligible_after_b011_canonical_closeout() -> None:",
            "    result = evaluate_task_snapshot(\"B012\", canonical_main=_CANONICAL_MAIN)",
            "",
            "    assert result[\"eligible\"] is True",
            "    assert result[\"state_consistency_result\"][\"observed_state\"] == \"PENDING\"",
            "    predecessor = next(row for row in result[\"prerequisite_results\"] if row[\"task_id\"] == \"B011\")",
            "    assert predecessor[\"satisfied\"] is True",
            "    assert \"task.blocked\" not in result[\"reasons\"]",
            "    assert \"task.unresolved_binding\" not in result[\"reasons\"]",
            "    validate_instance(\"mstr-task-eligibility-v0\", result)",
            "",
            "",
            "def test_b006_fails_closed_when_b005_discovery_manifest_is_missing",
        ]
    )
    contract, contract_count = contract_pattern.subn(contract_replacement, contract, count=1)
    assert contract_count == 1
    contract_path.write_text(contract, encoding="utf-8")

    cli_path = Path("tests/integration/test_task_gate_cli.py")
    cli = cli_path.read_text(encoding="utf-8")
    cli_pattern = re.compile(
        r"def test_task_eligible_b011_authorized_returns_zero\(.*?\n\n"
        r"def test_task_eligible_configuration_error_returns_two",
        re.S,
    )
    cli_replacement = "\n".join(
        [
            "def test_task_eligible_b011_terminal_returns_one(",
            "    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]",
            ") -> None:",
            "    expected = evaluate_task_snapshot(\"B011\", canonical_main=_CANONICAL_MAIN)",
            "",
            "    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:",
            "        assert task_id == \"B011\"",
            "        return expected",
            "",
            "    monkeypatch.setattr(",
            "        \"mstr_qualify.cli.evaluate_task_eligibility\", fake_evaluate_task_eligibility",
            "    )",
            "    exit_code = main([\"task\", \"eligible\", \"B011\"])",
            "    payload = _stdout_json(capsys)",
            "    assert exit_code == 1",
            "    assert payload == expected",
            "    assert payload[\"eligible\"] is False",
            "    assert \"task.already_terminal\" in payload[\"reasons\"]",
            "    validate_instance(\"mstr-task-eligibility-v0\", payload)",
            "",
            "",
            "def test_task_eligible_b012_successor_returns_zero(",
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
            "    assert exit_code == 0",
            "    assert payload == expected",
            "    assert payload[\"eligible\"] is True",
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
    old_convergence = '    assert tasks["B011"]["canonical_state"] == "PENDING"\n'
    assert convergence.count(old_convergence) == 1
    convergence = convergence.replace(
        old_convergence,
        (
            '    assert tasks["B011"]["canonical_state"] == "COMPLETE_CANONICAL"\n'
            '    assert tasks["B012"]["canonical_state"] == "PENDING"\n'
        ),
        1,
    )
    convergence_path.write_text(convergence, encoding="utf-8")


if __name__ == "__main__":
    main()
