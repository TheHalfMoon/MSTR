from __future__ import annotations

import copy
import json
import os
import subprocess
from pathlib import Path

ROOT = Path.cwd()
IMPLEMENTATION_HEAD = "da0480c0eb39e4097cb2d3fd3337a7fc49ab75dc"
IMPLEMENTATION_MERGE = "f71a15f967250c5c523749be9f9f3066feccb902"
ENTRY_GATE_MAIN = "fdca133e53a47b8966faef172812da58503576a0"
BUILDER_RUN_ID = os.environ["BUILDER_RUN_ID"]


def patch_catalog() -> None:
    path = ROOT / "configs/task-gate/mstr-000b.json"
    before = json.loads(path.read_text(encoding="utf-8"))
    after = copy.deepcopy(before)
    assert before["tasks"]["B023"]["canonical_state"] == "PENDING"
    after["tasks"]["B023"]["canonical_state"] = "COMPLETE_CANONICAL"
    for task_id, node in before["tasks"].items():
        expected = copy.deepcopy(node)
        if task_id == "B023":
            expected["canonical_state"] = "COMPLETE_CANONICAL"
        assert after["tasks"][task_id] == expected, task_id
    path.write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")


def patch_ledger() -> None:
    path = ROOT / "specs/002-code-model-supremacy-foundation/tasks.md"
    text = path.read_text(encoding="utf-8")
    open_line = "- [ ] **B023 Implement verifier-health evaluator on controlled fixtures.**  \n"
    closed_line = "- [x] **B023 Implement verifier-health evaluator on controlled fixtures.**\n"
    assert text.count(open_line) == 1, text.count(open_line)
    text = text.replace(open_line, closed_line, 1)

    output_line = (
        "  Outputs: verifier-health module/tests, "
        "`evidence/mstr-000b/B023-verifier-health-implementation.md`.\n"
    )
    provenance = (
        "  Canonical implementation: PR #133 / final head "
        f"`{IMPLEMENTATION_HEAD}` / merge `{IMPLEMENTATION_MERGE}`.\n"
    )
    assert text.count(output_line) == 1, text.count(output_line)
    text = text.replace(output_line, output_line + provenance, 1)
    assert "- [ ] **B024 Freeze test-generation curriculum and acceptance semantics.**" in text
    path.write_text(text, encoding="utf-8")


def patch_evidence() -> None:
    path = ROOT / "evidence/mstr-000b/B023-verifier-health-implementation.md"
    text = path.read_text(encoding="utf-8")
    state_line = "**State:** `IMPLEMENTATION_ACTIVE`"
    assert text.count(state_line) == 1
    header = (
        "**Implementation PR:** #133\n"
        f"**Final implementation head:** `{IMPLEMENTATION_HEAD}`\n"
        f"**Canonical implementation merge:** `{IMPLEMENTATION_MERGE}`\n"
        "**State:** COMPLETE_CANONICAL"
    )
    text = text.replace(state_line, header, 1)

    legacy_entry = f"ENTRY_CANONICAL_MAIN = {ENTRY_GATE_MAIN}\n"
    assert text.count(legacy_entry) == 1
    machine_entry = (
        "ENTRY_GATE_TASK = B023\n"
        f"ENTRY_GATE_CANONICAL_MAIN = {ENTRY_GATE_MAIN}\n"
        "ENTRY_GATE_ELIGIBLE = true\n"
    )
    assert "ENTRY_GATE_TASK = B023" not in text
    text = text.replace(legacy_entry, machine_entry + legacy_entry, 1)

    assert "## Canonical Implementation Closeout" not in text
    closeout = f"""
## Canonical Implementation Closeout

The B023 verifier-health evaluator was merged and independently verified on canonical main using controlled repository fixtures only. This closeout records canonical task and provenance state; it does not widen the evaluator into verifier execution, model execution, training, paid-compute, private-data, or production authority.

- implementation PR: `#133`
- final implementation head: `{IMPLEMENTATION_HEAD}`
- canonical implementation merge: `{IMPLEMENTATION_MERGE}`
- repaired atomic implementation build: run `33526148972` — SUCCESS
- exact-head qualification: run `33527138891` — SUCCESS
- exact-head independent review: review `5080178013` — NO ISSUES FOUND
- exact-head Cubic check: check `99921330743` — SUCCESS
- mandatory pre-merge verification: run `33528450915` — SUCCESS
- post-merge implementation verification: run `33528911288` — SUCCESS
- closeout builder negative evidence: runs `33529229275`, `33529850376`, `33530139830`, `33530762794`, `33530938623`, `33530974072`, `33531191471`, and `33532919817` — FAILURE / NO TARGET PUBLISHED
- repaired atomic closeout builder: run `{BUILDER_RUN_ID}` — candidate build in progress at commit construction

This closeout changes only B023 canonical state/provenance, the canonical task ledger, and closeout regression coverage. It does not modify the frozen B022 verifier-health schema, A006 protected terminal-success authority, A018 trajectory-admission authority, or B023 evaluator runtime. It grants no verifier subprocess execution, model execution, model-weight access, teacher/API execution, paid compute, network model calls, large/private/production data ingestion, weight-changing training, large-scale RL, candidate-pool authority change, or production release authority. B024 may become machine-eligible only because its exact prerequisite B023 is now canonically complete; B026 remains gated on B024.
"""
    path.write_text(text.rstrip() + "\n\n" + closeout.lstrip(), encoding="utf-8")


def patch_task_gate_tests() -> None:
    path = ROOT / "tests/contract/test_task_gate.py"
    text = path.read_text(encoding="utf-8")
    start_marker = "def test_b023_cross_workstream_prerequisites_are_canonically_bound() -> None:\n"
    end_marker = "def test_b025_is_terminal_after_canonical_closeout() -> None:\n"
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    replacement = '''def test_b023_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B023", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "A006",
        "A014",
        "B002",
        "B022",
    }
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)


def test_b023_closeout_opens_b024_as_next_machine_eligible_task() -> None:
    result = evaluate_task_snapshot("B024", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B023"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)


def test_b023_closeout_does_not_skip_b024_for_b026() -> None:
    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert "prerequisite.unsatisfied:B024" in result["reasons"]
    assert "prerequisite.unsatisfied:B022" not in result["reasons"]
    assert "prerequisite.unsatisfied:B025" not in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b023_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2]
        / "evidence"
        / "mstr-000b"
        / "B023-verifier-health-implementation.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #133" in evidence
    assert "`da0480c0eb39e4097cb2d3fd3337a7fc49ab75dc`" in evidence
    assert "`f71a15f967250c5c523749be9f9f3066feccb902`" in evidence
    assert "ENTRY_GATE_TASK = B023" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = fdca133e53a47b8966faef172812da58503576a0" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33526148972", "33527138891", "33528450915", "33528911288"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "review `5080178013` — NO ISSUES FOUND" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "VERIFIER_SUBPROCESS_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


'''
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def patch_cli_tests() -> None:
    path = ROOT / "tests/integration/test_task_gate_cli.py"
    text = path.read_text(encoding="utf-8")
    function_name = "def test_task_eligible_b023_terminal_returns_one("
    assert function_name not in text
    marker = "def test_task_eligible_b025_terminal_returns_one(\n"
    assert text.count(marker) == 1
    addition = '''def test_task_eligible_b023_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B023", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B023"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B023"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)


'''
    path.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")


def verify_scope() -> None:
    expected = sorted(
        [
            "configs/task-gate/mstr-000b.json",
            "evidence/mstr-000b/B023-verifier-health-implementation.md",
            "specs/002-code-model-supremacy-foundation/tasks.md",
            "tests/contract/test_task_gate.py",
            "tests/integration/test_task_gate_cli.py",
        ]
    )
    actual = sorted(
        subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    )
    assert actual == expected, (actual, expected)
    subprocess.run(["git", "diff", "--check"], check=True)


def main() -> None:
    patch_catalog()
    patch_ledger()
    patch_evidence()
    patch_task_gate_tests()
    patch_cli_tests()
    verify_scope()


if __name__ == "__main__":
    main()
