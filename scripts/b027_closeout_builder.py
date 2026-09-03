from __future__ import annotations

from pathlib import Path

EXPECTED_MAIN = "f667226dbf6cd380fefef5ff90fbc14eb1de3630"
IMPLEMENTATION_HEAD = "b5e152552f3b840fd74f2fe9b092eca17b56a91d"
ENTRY_MAIN = "312d40eee8400a0dab94633f891b206f66a82855"
TREE = "20e60c673a203e3fc7f09da817ffc6ad64ac5f76"


def replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


# Canonical task catalog: state-only closeout.
catalog = Path("configs/task-gate/mstr-000b.json")
text = catalog.read_text(encoding="utf-8")
text = replace_once(
    text,
    '    "B027": {\n      "canonical_state": "PENDING",',
    '    "B027": {\n      "canonical_state": "COMPLETE_CANONICAL",',
)
catalog.write_text(text, encoding="utf-8")

# Canonical task checklist + exact implementation provenance.
tasks = Path("specs/002-code-model-supremacy-foundation/tasks.md")
text = tasks.read_text(encoding="utf-8")
text = replace_once(
    text,
    "- [ ] **B027 Qualify the research ladder with one non-weight-changing campaign.**",
    "- [x] **B027 Qualify the research ladder with one non-weight-changing campaign.**",
)
outputs = "  Outputs: `artifacts/results/research/B027/`, `evidence/mstr-000b/B027-ladder-pilot.md`.\n"
text = replace_once(
    text,
    outputs,
    outputs
    + f"  Canonical implementation: PR #141 / final head `{IMPLEMENTATION_HEAD}` / merge `{EXPECTED_MAIN}`.\n",
)
tasks.write_text(text, encoding="utf-8")

# Evidence: immutable implementation identity and real-main acceptance.
evidence = Path("evidence/mstr-000b/B027-ladder-pilot.md")
text = evidence.read_text(encoding="utf-8")
old_top = (
    "**Task:** `B027`\n"
    "**State:** `IMPLEMENTATION_ACTIVE`\n"
    f"**Canonical entry main:** `{ENTRY_MAIN}`\n"
)
new_top = (
    "**Task:** `B027`\n"
    "**Implementation PR:** #141\n"
    f"**Final implementation head:** `{IMPLEMENTATION_HEAD}`\n"
    f"**Canonical implementation merge:** `{EXPECTED_MAIN}`\n"
    "**State:** COMPLETE_CANONICAL\n"
    f"**Canonical entry main:** `{ENTRY_MAIN}`\n"
)
text = replace_once(text, old_top, new_top)
gate_anchor = f"```text\nTASK = B027\nCANONICAL_MAIN = {ENTRY_MAIN}\n"
gate_repl = (
    "```text\n"
    "ENTRY_GATE_TASK = B027\n"
    f"ENTRY_GATE_CANONICAL_MAIN = {ENTRY_MAIN}\n"
    "ENTRY_GATE_ELIGIBLE = true\n"
    "TASK = B027\n"
    f"CANONICAL_MAIN = {ENTRY_MAIN}\n"
)
text = replace_once(text, gate_anchor, gate_repl)
old_tail = (
    "B027 remains `PENDING` in the canonical task ledger until this implementation is independently\n"
    "qualified, reviewed, merged, post-merge verified, and separately closed out.\n"
)
closeout = f"""## Canonical Implementation Closeout

The B027 bounded non-weight-changing research-ladder campaign is now accepted on canonical main.
This closeout records terminal task/provenance state only. It does not rerun or mutate the frozen
campaign, evaluator, schemas, promotion policies, material-result records, model/runtime surfaces,
or any authority artifact.

- implementation PR: `#141`
- final implementation head: `{IMPLEMENTATION_HEAD}`
- canonical implementation merge: `{EXPECTED_MAIN}`
- evaluator-affecting regeneration: run `33757330474` — SUCCESS
- exact-head qualification: run `33758435956` — SUCCESS
- exact-range independent review: CodeRabbit reviewed base `{ENTRY_MAIN}`, head `{IMPLEMENTATION_HEAD}`, tree `{TREE}`, 32 commits, and 60 changed files — NO ACTIONABLE COMMENTS
- mandatory exact-head pre-merge verification: run `33760082781` — SUCCESS
- real-main post-merge canonical verification: run `33761211923` — SUCCESS

Post-merge verification validated both B027 experiment records with full
`mstr.research-experiment.v2` semantics against real merged `main`, proved the campaign commits are
canonical ancestors, re-proved clean task drift and the pre-closeout B027 frontier, reran focused
and full quality gates, and preserved the zero-external-effect boundary. L0 remains the exact
`PROMOTE` result and L1 remains the exact controlled `STOP` on `code_proxy_thresholds`; L2/L3/L4
remain unexecuted. The premerge ledger fields such as `PENDING_POST_MERGE_VALIDATION` are immutable
historical candidate metadata and are not rewritten post hoc; canonical acceptance is recorded by
the guarded merge, post-merge proof, and this separate closeout.

This closeout grants no model-weight access, model execution, teacher/API execution, paid compute,
network model/teacher calls, data ingestion, verifier external effects, training/RL, Q4 execution,
or production release authority. B011, B013, B029, B030, and B031 remain governed by their own
canonical states and unresolved bindings.
"""
text = replace_once(text, old_tail, closeout)
evidence.write_text(text, encoding="utf-8")

# Contract regression: B027 is terminal and remains satisfied downstream.
test_path = Path("tests/contract/test_task_gate.py")
text = test_path.read_text(encoding="utf-8")
old_test = '''def test_b026_closeout_opens_b027_as_next_machine_eligible_task() -> None:
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
    validate_instance("mstr-task-eligibility-v0", result)
'''
new_test = '''def test_b027_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B027", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B026"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)


def test_b027_closeout_is_satisfied_for_b031_prerequisite() -> None:
    result = evaluate_task_snapshot("B031", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B027"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)
'''
text = replace_once(text, old_test, new_test)
marker = "\n\ndef test_b025_is_terminal_after_canonical_closeout() -> None:\n"
provenance = f'''

def test_b027_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2]
        / "evidence"
        / "mstr-000b"
        / "B027-ladder-pilot.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #141" in evidence
    assert "`{IMPLEMENTATION_HEAD}`" in evidence
    assert "`{EXPECTED_MAIN}`" in evidence
    assert "ENTRY_GATE_TASK = B027" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = {ENTRY_MAIN}" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33757330474", "33758435956", "33760082781", "33761211923"):
        assert f"run `{{run_id}}` — SUCCESS" in evidence
    assert "NO ACTIONABLE COMMENTS" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "RESEARCH_CAMPAIGN_EXTERNAL_EFFECT = NONE" in evidence
    assert "VERIFIER_EXTERNAL_EFFECT = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
'''
text = replace_once(text, marker, provenance + marker)
test_path.write_text(text, encoding="utf-8")

# CLI regression: terminal B027 returns exit code 1.
cli_path = Path("tests/integration/test_task_gate_cli.py")
text = cli_path.read_text(encoding="utf-8")
marker = "\n\ndef test_task_eligible_b025_terminal_returns_one(\n"
cli_test = '''

def test_task_eligible_b027_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B027", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B027"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B027"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)
'''
text = replace_once(text, marker, cli_test + marker)
cli_path.write_text(text, encoding="utf-8")
