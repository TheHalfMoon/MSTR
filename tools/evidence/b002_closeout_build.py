from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".")

IMPLEMENTATION_HEAD = "9905237b0685b50059112d19e2708ba6357283b6"
IMPLEMENTATION_MERGE = "298a97e957fe98edec2c9fdd3f78f0f909ec09fa"
FINAL_QUALIFICATION_RUN = "33081555793"
FINAL_QUALIFICATION_JOB = "98549853939"
POST_MERGE_RUN = "33081926043"
POST_MERGE_JOB = "98551169369"


def update_evidence() -> None:
    path = ROOT / "evidence/mstr-000b/B002-task-gate.md"
    path.write_text(
        f"""# B002 — Offline Task Eligibility Validator Canonical Evidence

**Workstream:** MSTR-000B
**Task:** B002
**State:** COMPLETE_CANONICAL
**Canonical implementation base:** `856a7993f64a7f17ead6f6c019c5668724444ed4`
**Implementation branch:** `feat/000b-b002-task-gate`
**Implementation PR:** `#48`
**Final implementation head:** `{IMPLEMENTATION_HEAD}`
**Canonical implementation merge:** `{IMPLEMENTATION_MERGE}`
**Final exact-head qualification run/job:** `{FINAL_QUALIFICATION_RUN}` / `{FINAL_QUALIFICATION_JOB}`
**Post-merge verification run/job:** `{POST_MERGE_RUN}` / `{POST_MERGE_JOB}`

This record closes B002 only when the separate closeout pull request containing this file, the canonical task checkbox, the machine task catalog state, and the closeout-aware regression tests is merged to canonical `main`. The implementation merge alone did not make B002 `COMPLETE_CANONICAL`.

## Bootstrap prerequisite

B002 was the second and final explicit machine-gate bootstrap exception. Before B002 execution, canonical main recorded B001 as `COMPLETE_CANONICAL`, with its canonical task checkbox checked and its post-merge closeout merged. B002 created no external-effect authority.

## Canonical implementation

PR #48 implemented the repository-local, read-only, fail-closed task eligibility validator and CLI gate. The implementation:

- loads the canonical MSTR-000B task catalog covering B001-B034;
- validates generated task nodes and eligibility results against the frozen machine contracts;
- exposes `python -m mstr_qualify task eligible <TASK_ID>` with exit contract `0=eligible`, `1=ineligible`, `2=configuration/contract error`;
- keeps live-main refresh/verification in the separate execution-governance step and then requires a clean local checkout with `HEAD == refs/heads/main == refs/remotes/origin/main`;
- rejects caller-controlled `--canonical-main` self-attestation;
- fails closed on unresolved or missing prerequisites, state/checkbox conflicts, undeclared terminal states, required output/evidence gaps, supersession, candidate-pool requirements, and external-effect authority requirements;
- rejects output/evidence/task-markdown/authority/candidate artifacts that traverse or resolve through symlinks outside the repository;
- validates exact authority binding, canonical authorization state, non-empty scope, explicit cost model, and finite non-negative resource ceilings with units;
- leaves unresolved future bindings explicitly blocked rather than inferring authority or cross-workstream prerequisites;
- performs no task-state, authority, candidate-pool, or external-effect mutation.

## Final exact-head qualification

A read-only evidence workflow checked out exact final implementation head `{IMPLEMENTATION_HEAD}` in detached-head mode, verified then-canonical main `856a7993f64a7f17ead6f6c019c5668724444ed4`, compiled the repaired contract source before test collection, and executed the frozen repository gates.

```text
FINAL_IMPLEMENTATION_HEAD = {IMPLEMENTATION_HEAD}
FINAL_EXACT_HEAD_RUN = {FINAL_QUALIFICATION_RUN}
FINAL_EXACT_HEAD_JOB = {FINAL_QUALIFICATION_JOB}
python -m py_compile tests/contract/test_task_gate.py = PASS
caller-supplied --canonical-main rejection = PASS / exit 2
TARGETED_TESTS = PASS (43 passed in 5.25s)
pytest -q = PASS (487 passed in 9.54s)
ruff check src tests = PASS
mypy = PASS (25 source files)
python -m mstr_qualify validate = PASS
VALID_FIXTURES_PASSED = 10
INVALID_FIXTURES_REJECTED = 10
FINAL_TARGET_SHA = {IMPLEMENTATION_HEAD}
```

## Final exact-head review

CodeRabbit re-reviewed exact head `{IMPLEMENTATION_HEAD}` against canonical main `856a7993f64a7f17ead6f6c019c5668724444ed4` after the last source repair and reported **no material issue in the reviewed offline task-gate boundary**. The prior malformed generated-test-source finding was verified directly against the Git blob and repaired before this final review. All inline review threads were resolved before merge. Historical findings on older heads are not reused as final-head evidence.

## Canonical implementation merge

Immediately before merge, live `main`, PR #48 head, mergeability, and review-thread state were re-read. PR #48 was merged with `expected_head_sha={IMPLEMENTATION_HEAD}`. GitHub then established:

```text
B002_IMPLEMENTATION_PR = 48
B002_FINAL_IMPLEMENTATION_HEAD = {IMPLEMENTATION_HEAD}
B002_IMPLEMENTATION_MERGE = {IMPLEMENTATION_MERGE}
POST_IMPLEMENTATION_MERGE_MAIN = {IMPLEMENTATION_MERGE}
PR_48_MERGED = YES
```

## Post-merge verification on canonical main

A separate read-only workflow checked out canonical `main` after the implementation merge and first proved:

```text
HEAD = refs/heads/main = refs/remotes/origin/main = {IMPLEMENTATION_MERGE}
WORKTREE = CLEAN
```

It then exercised the production B002 gate itself. The result was schema-valid, `task_id=B002`, `eligible=true`, `canonical_main={IMPLEMENTATION_MERGE}`, with B001 observed as `COMPLETE_CANONICAL` and satisfied. The same exact canonical main then passed:

```text
POST_MERGE_RUN = {POST_MERGE_RUN}
POST_MERGE_JOB = {POST_MERGE_JOB}
python -m py_compile tests/contract/test_task_gate.py = PASS
PRODUCTION_B002_ELIGIBILITY = PASS / eligible=true
TARGETED_TESTS = PASS (43 passed in 6.72s)
pytest -q = PASS (487 passed in 11.87s)
ruff check src tests = PASS
mypy = PASS (25 source files)
python -m mstr_qualify validate = PASS
VALID_FIXTURES_PASSED = 10
INVALID_FIXTURES_REJECTED = 10
FINAL_MAIN_SHA = {IMPLEMENTATION_MERGE}
```

## Closeout state transition

This closeout atomically aligns the human and machine sources of truth:

```text
B002_TASK_CHECKBOX = CHECKED
B002_MACHINE_CATALOG_STATE = COMPLETE_CANONICAL
B002_EVIDENCE_STATE = COMPLETE_CANONICAL
B002_EXECUTION_ELIGIBILITY_AFTER_CLOSEOUT = TERMINAL / NOT RE-EXECUTABLE
B003_PREREQUISITE_B002 = SATISFIED
```

The closeout regression coverage is updated accordingly: B002 is terminal and cannot be executed again, while B003 becomes the next eligible task in the MSTR-000B chain once this closeout is canonical on `main`. Before any B003 material mutation, execution governance must refresh/verify live main and the production `task eligible B003` command must return `eligible=true` on that exact main.

## Authority / non-goals

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

B002 authorizes none of the external-effect classes above. Successor tasks remain governed by their own prerequisites, candidate-pool requirements, authority requirements, and the exact live repository state.
""",
        encoding="utf-8",
    )


def update_tasks() -> None:
    path = ROOT / "specs/002-code-model-supremacy-foundation/tasks.md"
    text = path.read_text(encoding="utf-8")
    old = """- [ ] **B002 Implement offline task eligibility validator.**  \n  Conceptual CLI: `python -m mstr_qualify task eligible <TASK_ID>`. Fail closed on missing predecessor, stale/superseded task, missing explicit authority, candidate-pool prerequisite, or canonical-state conflict. Validator performs no mutation. B001/B002 bootstrap uses manual exact-prerequisite verification; after B002 becomes canonical there is no general bypass.  \n  Outputs: `src/mstr_qualify/task_gate.py`, CLI wiring, unit/contract tests, `evidence/mstr-000b/B002-task-gate.md`.\n"""
    new = f"""- [x] **B002 Implement offline task eligibility validator.**\n  Conceptual CLI: `python -m mstr_qualify task eligible <TASK_ID>`. Fail closed on missing predecessor, stale/superseded task, missing explicit authority, candidate-pool prerequisite, or canonical-state conflict. Validator performs no mutation. B001/B002 bootstrap uses manual exact-prerequisite verification; after B002 becomes canonical there is no general bypass.\n  Outputs: `src/mstr_qualify/task_gate.py`, CLI wiring, unit/contract tests, `evidence/mstr-000b/B002-task-gate.md`.\n  Canonical implementation: PR #48 / final head `{IMPLEMENTATION_HEAD}` / merge `{IMPLEMENTATION_MERGE}`.\n"""
    if text.count(old) != 1:
        raise SystemExit(f"B002 tasks block match count: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_catalog() -> None:
    path = ROOT / "configs/task-gate/mstr-000b.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    state = data["tasks"]["B002"]["canonical_state"]
    if state != "PENDING":
        raise SystemExit(f"unexpected B002 catalog state: {state!r}")
    data["tasks"]["B002"]["canonical_state"] = "COMPLETE_CANONICAL"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_contract_tests() -> None:
    path = ROOT / "tests/contract/test_task_gate.py"
    text = path.read_text(encoding="utf-8")
    old_state = '    assert catalog.nodes["B002"]["canonical_state"] == "PENDING"\n'
    new_state = '    assert catalog.nodes["B002"]["canonical_state"] == "COMPLETE_CANONICAL"\n'
    if text.count(old_state) != 1:
        raise SystemExit(f"B002 catalog assertion match count: {text.count(old_state)}")
    text = text.replace(old_state, new_state, 1)

    old_tests = '''def test_b002_is_bootstrap_eligible_from_canonical_b001() -> None:\n    result = evaluate_task_snapshot("B002", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is True\n    assert result["prerequisite_results"][0]["task_id"] == "B001"\n    assert result["prerequisite_results"][0]["satisfied"] is True\n    assert result["reasons"] == []\n    validate_instance("mstr-task-eligibility-v0", result)\n\n\ndef test_b003_fails_closed_until_b002_closeout_is_canonical() -> None:\n    result = evaluate_task_snapshot("B003", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is False\n    assert result["prerequisite_results"][0]["task_id"] == "B002"\n    assert result["prerequisite_results"][0]["observed_state"] == "PENDING"\n    assert result["prerequisite_results"][0]["satisfied"] is False\n    assert "prerequisite.unsatisfied:B002" in result["reasons"]\n    validate_instance("mstr-task-eligibility-v0", result)\n'''
    new_tests = '''def test_b002_is_terminal_after_canonical_closeout() -> None:\n    result = evaluate_task_snapshot("B002", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is False\n    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"\n    assert result["state_consistency_result"]["satisfied"] is True\n    assert "task.already_terminal" in result["reasons"]\n    validate_instance("mstr-task-eligibility-v0", result)\n\n\ndef test_b003_is_eligible_after_b002_closeout_is_canonical() -> None:\n    result = evaluate_task_snapshot("B003", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is True\n    assert result["prerequisite_results"][0]["task_id"] == "B002"\n    assert result["prerequisite_results"][0]["observed_state"] == "COMPLETE_CANONICAL"\n    assert result["prerequisite_results"][0]["satisfied"] is True\n    assert result["reasons"] == []\n    validate_instance("mstr-task-eligibility-v0", result)\n'''
    if text.count(old_tests) != 1:
        raise SystemExit(f"B002/B003 test block match count: {text.count(old_tests)}")
    path.write_text(text.replace(old_tests, new_tests, 1), encoding="utf-8")


def main() -> None:
    update_evidence()
    update_tasks()
    update_catalog()
    update_contract_tests()


if __name__ == "__main__":
    main()
