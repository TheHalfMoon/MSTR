from __future__ import annotations

import json
from pathlib import Path

BASE_MAIN = "138a2c2c1d86c050db79e3190ab24d7c1052fe44"
IMPLEMENTATION_HEAD = "fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2"
IMPLEMENTATION_PR = 135
POSTMERGE_RUN = 33560182387


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
    path.write_text(text[:start_index] + replacement + "\n\n" + text[end_index:], encoding="utf-8")


def update_catalog() -> None:
    path = Path("configs/task-gate/mstr-000b.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    task = payload["tasks"]["B024"]
    if task["canonical_state"] != "PENDING":
        raise RuntimeError(f"unexpected B024 state: {task['canonical_state']}")
    if task.get("prerequisites") != ["B023"]:
        raise RuntimeError(f"unexpected B024 prerequisites: {task.get('prerequisites')}")
    task["canonical_state"] = "COMPLETE_CANONICAL"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_tasks() -> None:
    path = Path("specs/002-code-model-supremacy-foundation/tasks.md")
    replace_once(
        path,
        "- [ ] **B024 Freeze test-generation curriculum and acceptance semantics.**  \n",
        "- [x] **B024 Freeze test-generation curriculum and acceptance semantics.**\n",
    )
    replace_once(
        path,
        "  Outputs: `docs/data/TEST_GENERATION_CURRICULUM.md`, fixtures, `evidence/mstr-000b/B024-test-curriculum.md`.\n\n- [x] **B025 Freeze greenfield/feature/synthesis curriculum.**",
        "  Outputs: `docs/data/TEST_GENERATION_CURRICULUM.md`, fixtures, `evidence/mstr-000b/B024-test-curriculum.md`.\n"
        "  Canonical implementation: PR #135 / final head `fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2` / merge `138a2c2c1d86c050db79e3190ab24d7c1052fe44`.\n\n"
        "- [x] **B025 Freeze greenfield/feature/synthesis curriculum.**",
    )


def update_evidence() -> None:
    path = Path("evidence/mstr-000b/B024-test-curriculum.md")
    replace_once(
        path,
        "**Task:** `B024`\n**State:** `IMPLEMENTATION_ACTIVE`\n",
        "**Task:** `B024`\n"
        "**Implementation PR:** #135\n"
        "**Final implementation head:** `fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2`\n"
        "**Canonical implementation merge:** `138a2c2c1d86c050db79e3190ab24d7c1052fe44`\n"
        "**State:** COMPLETE_CANONICAL\n",
    )
    replace_once(
        path,
        "```text\nTASK = B024\nCANONICAL_MAIN = 1ffa71c94bda161ec7be7784de3a6a4be81570ad\n",
        "```text\n"
        "ENTRY_GATE_TASK = B024\n"
        "ENTRY_GATE_CANONICAL_MAIN = 1ffa71c94bda161ec7be7784de3a6a4be81570ad\n"
        "ENTRY_GATE_ELIGIBLE = true\n"
        "TASK = B024\n"
        "CANONICAL_MAIN = 1ffa71c94bda161ec7be7784de3a6a4be81570ad\n",
    )
    text = path.read_text(encoding="utf-8")
    if "## Canonical Implementation Closeout" in text:
        raise RuntimeError("B024 closeout section already present")
    closeout = """

## Canonical Implementation Closeout

The B024 test-generation curriculum and acceptance contract were merged and independently verified on canonical main. This closeout records terminal task/provenance state only. It does not authorize test generation with a model, verifier execution, model execution, model-weight access, training, paid compute, external/private data ingestion, candidate-pool changes, or production release.

- implementation PR: `#135`
- final implementation head: `fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2`
- canonical implementation merge: `138a2c2c1d86c050db79e3190ab24d7c1052fe44`
- guarded final repair builder: run `33553919725` — SUCCESS
- exact-head qualification: run `33554572587` — SUCCESS
- exact-head independent review: CodeRabbit comment `5498547347` / run `e2805914-59c9-4314-99e2-04bcb3ed5892` — NO ACTIONABLE COMMENTS
- mandatory pre-merge verification: run `33559716801` — SUCCESS
- post-merge implementation verification: run `33560182387` — SUCCESS

The fresh Codex review request on the final head was service-blocked by the Codex code-review usage limit, so it was not represented as successful review evidence. The independent exact-head CodeRabbit review explicitly reviewed the exact base-to-head range and all 11 changed files. Its non-blocking future-risk note about authenticated producer provenance does not grant or imply runtime/training authority; authenticated evidence provenance remains a future consumer-side hardening requirement before any admission path may rely on such evidence.

This closeout changes only B024 canonical state/provenance, the canonical task ledger, and closeout regression coverage. The frozen B024 runtime/design schemas and semantic validator are unchanged by this closeout. B026 may become machine-eligible only because B022, B024, and B025 are now canonically complete. B011 remains separately blocked on repository-specific external authority.
"""
    path.write_text(text.rstrip() + closeout + "\n", encoding="utf-8")


def update_contract_tests() -> None:
    path = Path("tests/contract/test_task_gate.py")
    replace_function(
        path,
        "def test_b023_closeout_opens_b024_as_next_machine_eligible_task() -> None:\n",
        "def test_b023_closeout_does_not_skip_b024_for_b026() -> None:\n",
        '''def test_b024_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B024", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B023"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)''',
    )
    replace_function(
        path,
        "def test_b023_closeout_does_not_skip_b024_for_b026() -> None:\n",
        "def test_b023_closeout_provenance_and_authority_boundary() -> None:\n",
        '''def test_b024_closeout_opens_b026_as_next_machine_eligible_task() -> None:
    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert result["authority_result"]["required"] is False
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "B022",
        "B024",
        "B025",
    }
    assert all(item["observed_state"] == "COMPLETE_CANONICAL" for item in result["prerequisite_results"])
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)''',
    )
    insertion_marker = "def test_b025_is_terminal_after_canonical_closeout() -> None:\n"
    text = path.read_text(encoding="utf-8")
    if text.count(insertion_marker) != 1:
        raise RuntimeError("unexpected B025 terminal-test marker count")
    provenance_test = '''def test_b024_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2]
        / "evidence"
        / "mstr-000b"
        / "B024-test-curriculum.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #135" in evidence
    assert "`fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2`" in evidence
    assert "`138a2c2c1d86c050db79e3190ab24d7c1052fe44`" in evidence
    assert "ENTRY_GATE_TASK = B024" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 1ffa71c94bda161ec7be7784de3a6a4be81570ad" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33553919725", "33554572587", "33559716801", "33560182387"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "CodeRabbit comment `5498547347`" in evidence
    assert "e2805914-59c9-4314-99e2-04bcb3ed5892" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "TEST_GENERATION_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


'''
    path.write_text(text.replace(insertion_marker, provenance_test + insertion_marker), encoding="utf-8")
    replace_function(
        path,
        "def test_b025_closeout_satisfies_only_its_b026_prerequisite() -> None:\n",
        "def test_b028_is_terminal_after_canonical_closeout() -> None:\n",
        '''def test_b025_prerequisite_remains_satisfied_after_b024_closeout() -> None:
    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B025")
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
    test = '''def test_task_eligible_b024_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B024", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B024"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B024"])
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
