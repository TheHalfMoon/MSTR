from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


# Canonical task state: only B019 transitions to terminal.
path = "configs/task-gate/mstr-000b.json"
text = read(path)
old = '    "B019": {\n      "canonical_state": "PENDING",'
new = '    "B019": {\n      "canonical_state": "COMPLETE_CANONICAL",'
assert text.count(old) == 1
write(path, text.replace(old, new, 1))

# Human task ledger: close B019 and bind canonical implementation provenance.
path = "specs/002-code-model-supremacy-foundation/tasks.md"
text = read(path)
old = "- [ ] **B019 Freeze bounded teacher-rescue policy.**  \n"
new = "- [x] **B019 Freeze bounded teacher-rescue policy.**\n"
assert text.count(old) == 1
text = text.replace(old, new, 1)
needle = (
    "  Outputs: `docs/data/TEACHER_RESCUE_POLICY.md`, schema/fixtures, "
    "`evidence/mstr-000b/B019-teacher-policy.md`.\n"
)
assert text.count(needle) == 1
text = text.replace(
    needle,
    needle
    + "  Canonical implementation: PR #78 / final head "
    "`25907c32fb60e83a6b171192e8c12c8092bc9f5e` / merge "
    "`ac68e2ff9de9962807ab32ce983b2e808bf4fab9`.\n",
    1,
)
write(path, text)

# Evidence ledger: bind exact implementation and verification provenance.
path = "evidence/mstr-000b/B019-teacher-policy.md"
text = read(path)
old = (
    "**Task:** `B019`\n"
    "**State:** IMPLEMENTATION_CANDIDATE\n"
    "**Contract:** `mstr.teacher-rescue-record.v0`\n"
)
new = (
    "**Task:** `B019`\n"
    "**Implementation PR:** #78\n"
    "**Final implementation head:** `25907c32fb60e83a6b171192e8c12c8092bc9f5e`\n"
    "**Canonical implementation merge:** `ac68e2ff9de9962807ab32ce983b2e808bf4fab9`\n"
    "**State:** COMPLETE_CANONICAL\n"
    "**Contract:** `mstr.teacher-rescue-record.v0`\n"
)
assert text.count(old) == 1
text = text.replace(old, new, 1)
closeout = """
## Canonical Implementation Closeout

The bounded teacher-rescue contract was merged without widening authority, data scope, or external effects.

- implementation PR: `#78`
- final implementation head: `25907c32fb60e83a6b171192e8c12c8092bc9f5e`
- canonical implementation merge: `ac68e2ff9de9962807ab32ce983b2e808bf4fab9`
- exact-final-head qualification: run `33193446438` — SUCCESS
- independent adversarial review: run `33193784736` / job `98925641414` — SUCCESS
- mandatory pre-merge verification: run `33193968205` — SUCCESS
- post-merge implementation verification: run `33194149258` — SUCCESS

This closeout changes only canonical task/provenance state and regression assertions. It grants no model-weight access, teacher/model/API execution, paid compute, network teacher calls, large-data ingestion, weight-changing training, B020 difficulty-calibration authority, B022 verifier-health authority, or production release authority. B011 remains blocked.
"""
assert "## Canonical Implementation Closeout" not in text
write(path, text.rstrip() + "\n\n" + closeout.lstrip())

# B019-specific provenance regression.
path = "tests/contract/test_teacher_rescue_contract.py"
text = read(path)
assert "test_b019_canonical_closeout_provenance_and_authority_boundary" not in text
append = '''


def test_b019_canonical_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        ROOT / "evidence" / "mstr-000b" / "B019-teacher-policy.md"
    ).read_text(encoding="utf-8")
    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #78" in evidence
    assert (
        "**Final implementation head:** "
        "`25907c32fb60e83a6b171192e8c12c8092bc9f5e`" in evidence
    )
    assert (
        "**Canonical implementation merge:** "
        "`ac68e2ff9de9962807ab32ce983b2e808bf4fab9`" in evidence
    )
    assert "run `33193446438` — SUCCESS" in evidence
    assert "run `33193784736` / job `98925641414` — SUCCESS" in evidence
    assert "run `33193968205` — SUCCESS" in evidence
    assert "run `33194149258` — SUCCESS" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "TEACHER_API_EXECUTION = NONE" in evidence
    assert "PAID_MODEL_API = NONE" in evidence
    assert "NETWORK_TEACHER_CALL = NONE" in evidence
    assert "LARGE_DATASET_INGESTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE" in evidence
    assert "B022_VERIFIER_HEALTH_AUTHORITY = NONE" in evidence
'''
write(path, text.rstrip() + append + "\n")

# Machine task-gate regression: B019 is terminal after canonical closeout.
path = "tests/contract/test_task_gate.py"
text = read(path)
old = '''def test_b018_closeout_opens_b019_teacher_policy() -> None:
    result = evaluate_task_snapshot("B019", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert result["authority_result"]["required"] is False
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B018"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", result)
'''
new = '''def test_b019_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B019", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B018"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", result)
'''
assert text.count(old) == 1
write(path, text.replace(old, new, 1))

# CLI terminal behavior regression.
path = "tests/integration/test_task_gate_cli.py"
text = read(path)
assert "test_task_eligible_b019_terminal_returns_one" not in text
append = '''


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
'''
write(path, text.rstrip() + append + "\n")
