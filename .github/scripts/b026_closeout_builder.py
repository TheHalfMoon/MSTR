from __future__ import annotations

import json
from pathlib import Path

BASE_MAIN = "1aed67793fa14e6c9a7bbe4067ad521d16617b26"
IMPLEMENTATION_HEAD = "ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421"
IMPLEMENTATION_PR = 137
POSTMERGE_RUN = 33683456723


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match in {path}, found {count}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def replace_function(path: Path, start: str, next_start: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    start_index = text.find(start)
    if start_index < 0:
        raise RuntimeError(f"missing function marker in {path}: {start}")
    end_index = text.find(next_start, start_index + len(start))
    if end_index < 0:
        raise RuntimeError(f"missing next function marker in {path}: {next_start}")
    path.write_text(text[:start_index] + replacement.rstrip() + "\n\n\n" + text[end_index:], encoding="utf-8")


def update_catalog() -> None:
    path = Path("configs/task-gate/mstr-000b.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    task = payload["tasks"]["B026"]
    if task["canonical_state"] != "PENDING":
        raise RuntimeError(f"unexpected B026 state: {task['canonical_state']}")
    if task.get("prerequisites") != ["B022", "B024", "B025"]:
        raise RuntimeError(f"unexpected B026 prerequisites: {task.get('prerequisites')}")
    task["canonical_state"] = "COMPLETE_CANONICAL"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_tasks() -> None:
    path = Path("specs/002-code-model-supremacy-foundation/tasks.md")
    replace_once(
        path,
        "- [ ] **B026 Freeze multi-fidelity MSTR Research Ladder v0.**  \n",
        "- [x] **B026 Freeze multi-fidelity MSTR Research Ladder v0.**\n",
    )
    replace_once(
        path,
        "  Outputs: contract/config, `evidence/mstr-000b/B026-research-ladder.md`.\n\n- [ ] **B027 Qualify the research ladder with one non-weight-changing campaign.**",
        "  Outputs: contract/config, `evidence/mstr-000b/B026-research-ladder.md`.\n"
        "  Canonical implementation: PR #137 / final head `ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421` / merge `1aed67793fa14e6c9a7bbe4067ad521d16617b26`.\n\n"
        "- [ ] **B027 Qualify the research ladder with one non-weight-changing campaign.**",
    )


def update_evidence() -> None:
    path = Path("evidence/mstr-000b/B026-research-ladder.md")
    replace_once(
        path,
        "**Task:** `B026`\n**State:** `IMPLEMENTATION_ACTIVE`\n",
        "**Task:** `B026`\n"
        "**Implementation PR:** #137\n"
        "**Final implementation head:** `ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421`\n"
        "**Canonical implementation merge:** `1aed67793fa14e6c9a7bbe4067ad521d16617b26`\n"
        "**State:** COMPLETE_CANONICAL\n",
    )
    replace_once(
        path,
        "```text\nTASK = B026\nCANONICAL_MAIN = 823cd7ec3b4c537876a0795d0f0f8d4bd75acd85\n",
        "```text\n"
        "ENTRY_GATE_TASK = B026\n"
        "ENTRY_GATE_CANONICAL_MAIN = 823cd7ec3b4c537876a0795d0f0f8d4bd75acd85\n"
        "ENTRY_GATE_ELIGIBLE = true\n"
        "TASK = B026\n"
        "CANONICAL_MAIN = 823cd7ec3b4c537876a0795d0f0f8d4bd75acd85\n",
    )
    text = path.read_text(encoding="utf-8")
    if "## Canonical Implementation Closeout" in text:
        raise RuntimeError("B026 closeout section already present")
    closeout = """

## Canonical Implementation Closeout

The B026 Multi-Fidelity MSTR Research Ladder v0 contract/configuration implementation merged and was re-verified on canonical main. This closeout records terminal task/provenance state only. It does not execute B027 and does not authorize model execution, model-weight access, verifier execution, teacher/API execution, paid compute/API, network model/teacher calls, data ingestion, training/RL, Q4 execution, or production release.

- implementation PR: `#137`
- final implementation head: `ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421`
- canonical implementation merge: `1aed67793fa14e6c9a7bbe4067ad521d16617b26`
- guarded final causal-ordering repair builder: run `33677458758` — SUCCESS
- exact-head qualification: run `33678090319` — SUCCESS
- exact-head independent review: CodeRabbit comment `5516237548` — NO ACTIONABLE COMMENTS on exact base/head/tree, 9 commits, and all 17 changed files
- mandatory exact-head pre-merge verification: run `33682188378` — SUCCESS
- post-merge implementation verification: run `33683456723` — SUCCESS

The final implementation review confirms canonical Git-blob resolution, strict campaign-freeze/evidence ordering, predecessor-evidence causality, verifier-evidence derivation, governed-effect authority binding, positive-network-byte effect derivation, and L4/Q4 identity controls. Earlier-head findings remain historical and are not represented as current findings.

This closeout changes only B026 canonical state/provenance, the canonical task ledger, and closeout regression coverage. The frozen B026 schemas, semantic validator, ladder configuration, and source implementation are unchanged by this closeout. B027 becomes machine-eligible only because B026 is now canonically complete. B011 remains separately blocked on repository-specific external authority.
"""
    path.write_text(text.rstrip() + closeout.rstrip() + "\n", encoding="utf-8")


def update_contract_tests() -> None:
    path = Path("tests/contract/test_task_gate.py")
    replace_function(
        path,
        "def test_b024_closeout_opens_b026_as_next_machine_eligible_task() -> None:\n",
        "def test_b023_closeout_provenance_and_authority_boundary() -> None:\n",
        '''def test_b026_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "B022",
        "B024",
        "B025",
    }
    assert all(
        item["observed_state"] == "COMPLETE_CANONICAL"
        for item in result["prerequisite_results"]
    )
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)


def test_b026_closeout_opens_b027_as_next_machine_eligible_task() -> None:
    result = evaluate_task_snapshot("B027", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert result["authority_result"]["required"] is False
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B026"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)''',
    )
    marker = "def test_b025_is_terminal_after_canonical_closeout() -> None:\n"
    text = path.read_text(encoding="utf-8")
    if text.count(marker) != 1:
        raise RuntimeError("unexpected B025 terminal marker count")
    provenance = '''def test_b026_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2]
        / "evidence"
        / "mstr-000b"
        / "B026-research-ladder.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #137" in evidence
    assert "`ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421`" in evidence
    assert "`1aed67793fa14e6c9a7bbe4067ad521d16617b26`" in evidence
    assert "ENTRY_GATE_TASK = B026" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 823cd7ec3b4c537876a0795d0f0f8d4bd75acd85" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33677458758", "33678090319", "33682188378", "33683456723"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "CodeRabbit comment `5516237548`" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "RESEARCH_CAMPAIGN_EXECUTION = NONE" in evidence
    assert "VERIFIER_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


'''
    path.write_text(text.replace(marker, provenance + marker), encoding="utf-8")
    replace_function(
        path,
        "def test_b025_prerequisite_remains_satisfied_after_b024_closeout() -> None:\n",
        "def test_b028_is_terminal_after_canonical_closeout() -> None:\n",
        '''def test_b025_prerequisite_remains_recorded_after_b026_closeout() -> None:
    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B025"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)''',
    )


def update_cli_tests() -> None:
    path = Path("tests/integration/test_task_gate_cli.py")
    marker = "def test_task_eligible_b025_terminal_returns_one(\n"
    text = path.read_text(encoding="utf-8")
    if text.count(marker) != 1:
        raise RuntimeError("unexpected B025 CLI marker count")
    test = '''def test_task_eligible_b026_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B026"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B026"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


'''
    path.write_text(text.replace(marker, test + marker), encoding="utf-8")


def main() -> None:
    update_catalog()
    update_tasks()
    update_evidence()
    update_contract_tests()
    update_cli_tests()


if __name__ == "__main__":
    main()
