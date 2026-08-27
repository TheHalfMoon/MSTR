from __future__ import annotations

import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} match count: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


catalog = Path("configs/task-gate/mstr-000b.json")
payload = json.loads(catalog.read_text(encoding="utf-8"))
assert payload["tasks"]["B003"]["canonical_state"] == "PENDING"
payload["tasks"]["B003"]["canonical_state"] = "COMPLETE_CANONICAL"
catalog.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

tasks = Path("specs/002-code-model-supremacy-foundation/tasks.md")
replace_once(
    tasks,
    "- [ ] **B003 Implement canonical drift detector.**  \n"
    "  Prerequisite: B002 `COMPLETE_CANONICAL` and an exact-main `eligible=true` result. Compare task checkboxes/state/evidence/PR merge records where machine-readable. Detect examples such as implementation merged while task remains active, or task executed before declared entry gate.  \n"
    "  Outputs: `src/mstr_qualify/task_drift.py`, tests/fixtures, `evidence/mstr-000b/B003-drift-detector.md`.\n",
    "- [x] **B003 Implement canonical drift detector.**\n"
    "  Prerequisite: B002 `COMPLETE_CANONICAL` and an exact-main `eligible=true` result. Compare task checkboxes/state/evidence/PR merge records where machine-readable. Detect examples such as implementation merged while task remains active, or task executed before declared entry gate.\n"
    "  Outputs: `src/mstr_qualify/task_drift.py`, tests/fixtures, `evidence/mstr-000b/B003-drift-detector.md`.\n"
    "  Canonical implementation: PR #50 / final head `f3ccad9d49ea9d0460f82d7ecfe64b649bd997cf` / merge `8bea74269fb81a4c898b7a2864bf103d15fd98a9`.\n",
    "B003 task closeout",
)

evidence = Path("evidence/mstr-000b/B003-drift-detector.md")
evidence.write_text(
    """# B003 — Canonical Drift Detector Closeout Evidence

**Workstream:** MSTR-000B
**Task:** B003
**State:** COMPLETE_CANONICAL
**Implementation branch:** `feat/000b-b003-drift-detector`
**Implementation PR:** `#50`
**Final implementation head:** `f3ccad9d49ea9d0460f82d7ecfe64b649bd997cf`
**Canonical implementation merge:** `8bea74269fb81a4c898b7a2864bf103d15fd98a9`

## Mandatory exact-main entry gate

```text
ENTRY_GATE_TASK = B003
ENTRY_GATE_CANONICAL_MAIN = 0754d552752c2f6c099df2b480de99028e2e26e5
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_RUN = 33083687113
ENTRY_GATE_JOB = 98557431219
```

B003 implementation began only after B002 was `COMPLETE_CANONICAL` and the exact-main production task gate returned `eligible=true`.

## Final implementation qualification

Exact-head qualification run `33091769930`, job `98586178496`, checked out final implementation head `f3ccad9d49ea9d0460f82d7ecfe64b649bd997cf` detached and verified canonical entry main `0754d552752c2f6c099df2b480de99028e2e26e5`.

```text
B003_FIXTURE_CASES = 13
B003_TARGETED_TESTS = PASS (9 passed)
B003_EXACT_MAIN_ELIGIBLE = true
CANONICAL_DRIFT_STATUS = clean
pytest -q = PASS (496 passed)
ruff check src tests = PASS
mypy = PASS (26 source files)
python -m mstr_qualify validate = PASS
VALID_FIXTURES = 10
INVALID_FIXTURES_REJECTED = 10
FINAL_B003_SHA = f3ccad9d49ea9d0460f82d7ecfe64b649bd997cf
FINAL_MAIN_SHA = 0754d552752c2f6c099df2b480de99028e2e26e5
```

Fresh CodeRabbit exact-head review on `f3ccad9d49ea9d0460f82d7ecfe64b649bd997cf` found no material issue after the review-driven fail-closed and terminal-state repairs. Existing inline review threads were resolved before merge.

Pre-merge gate v2 run `33092154255` re-proved production `task eligible B003 => true` on live main and used the exact feature-head detector to prove canonical drift was clean immediately before merge.

## Canonical implementation merge and post-merge proof

PR #50 merged with expected-head guard on exact `f3ccad9d49ea9d0460f82d7ecfe64b649bd997cf`, producing canonical merge `8bea74269fb81a4c898b7a2864bf103d15fd98a9`.

Post-merge verification run `33092318536`, job `98588109465`, executed on exact canonical main `8bea74269fb81a4c898b7a2864bf103d15fd98a9` and passed:

```text
POSTMERGE_B003_ELIGIBLE_PENDING_CLOSEOUT = true
POSTMERGE_DRIFT_CODES = entry_gate.final_head_missing,evidence.implementation_identity_missing,implementation.merged_while_active
B003_TARGETED_TESTS = PASS (9 passed)
pytest -q = PASS (496 passed)
ruff check src tests = PASS
mypy = PASS (26 source files)
python -m mstr_qualify validate = PASS
FINAL_MAIN_SHA = 8bea74269fb81a4c898b7a2864bf103d15fd98a9
```

Those three drift findings are the expected pre-closeout state: implementation was merged while B003 remained active and the implementation identities had not yet been canonicalized. This closeout aligns the task checkbox, machine catalog, task implementation record, and evidence identities so the detector can prove the resulting candidate state clean.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API_EXECUTION = NONE
PAID_COMPUTE = NONE
RENTED_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
PRIVATE_USER_TRACE_INGESTION = NONE
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

## Closeout rule

This document becomes canonical only after the separate B003 closeout PR itself passes exact-head qualification and review, merges with an expected-head guard, and post-closeout canonical main proves: B003 is terminal, B004 is `eligible=true`, `task drift` is `clean`, and all frozen repository gates pass. Until that merge and post-closeout verification, B003 remains a closeout candidate rather than a completed claim.
""",
    encoding="utf-8",
)

contract = Path("tests/contract/test_task_gate.py")
replace_once(
    contract,
    '    assert catalog.nodes["B001"]["canonical_state"] == "COMPLETE_CANONICAL"\n'
    '    assert catalog.nodes["B002"]["canonical_state"] == "COMPLETE_CANONICAL"\n',
    '    assert catalog.nodes["B001"]["canonical_state"] == "COMPLETE_CANONICAL"\n'
    '    assert catalog.nodes["B002"]["canonical_state"] == "COMPLETE_CANONICAL"\n'
    '    assert catalog.nodes["B003"]["canonical_state"] == "COMPLETE_CANONICAL"\n',
    "catalog B003 canonical assertion",
)
replace_once(
    contract,
    '''def test_b003_is_eligible_after_b002_closeout_is_canonical() -> None:
    result = evaluate_task_snapshot("B003", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["prerequisite_results"][0]["task_id"] == "B002"
    assert result["prerequisite_results"][0]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["prerequisite_results"][0]["satisfied"] is True
    assert result["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", result)
''',
    '''def test_b003_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B003", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b004_is_eligible_after_b003_closeout_is_canonical() -> None:
    result = evaluate_task_snapshot("B004", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["prerequisite_results"][0]["task_id"] == "B003"
    assert result["prerequisite_results"][0]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["prerequisite_results"][0]["satisfied"] is True
    assert result["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", result)
''',
    "B003/B004 contract transition",
)

integration = Path("tests/integration/test_task_gate_cli.py")
replace_once(
    integration,
    '''def test_task_eligible_b003_successor_returns_zero(
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

    assert exit_code == 0
    assert payload == expected
    assert payload["eligible"] is True
    assert payload["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", payload)
''',
    '''def test_task_eligible_b003_terminal_returns_one(
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


def test_task_eligible_b004_successor_returns_zero(
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

    assert exit_code == 0
    assert payload == expected
    assert payload["eligible"] is True
    assert payload["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", payload)
''',
    "B003/B004 CLI transition",
)
