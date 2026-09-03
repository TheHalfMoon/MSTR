from __future__ import annotations

import json
import re
from pathlib import Path

CONFIG = Path("configs/task-gate/mstr-000b.json")
TASKS = Path("specs/002-code-model-supremacy-foundation/tasks.md")
EVIDENCE = Path("evidence/mstr-000b/B029-adaptive-inference.md")
TASK_TESTS = Path("tests/contract/test_task_gate.py")
CONVERGENCE_TESTS = Path("tests/contract/test_convergence_external_bindings.py")

FINAL_HEAD = "f449f81fc3e7343052b54b09b0481d64963d7e2f"
MERGE_SHA = "b3223bb384d8723c37a28526be691cedf8174dc3"


def update_catalog() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    node = payload["tasks"]["B029"]
    if node["canonical_state"] != "PENDING":
        raise SystemExit(f"unexpected B029 state: {node['canonical_state']}")
    node["canonical_state"] = "COMPLETE_CANONICAL"
    CONFIG.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_tasks() -> None:
    text = TASKS.read_text(encoding="utf-8")
    marker = "- [ ] **B029 Freeze adaptive test-time compute + selective-context policy.**"
    checked = marker.replace("[ ]", "[x]")
    if text.count(marker) != 1:
        raise SystemExit(f"pending B029 marker count={text.count(marker)}")
    text = text.replace(marker, checked, 1)
    text, cleaned = re.subn(
        rf"({re.escape(checked)})[ \t]+(?=\n)",
        r"\1",
        text,
        count=1,
    )
    if cleaned != 1:
        raise SystemExit("expected one B029 task-line whitespace normalization")
    pattern = re.compile(
        r"(- \[x\] \*\*B029 Freeze adaptive test-time compute \+ selective-context policy\.\*\*.*?)(?=\n- \[[ x]\] \*\*B030)",
        re.S,
    )
    match = pattern.search(text)
    if match is None:
        raise SystemExit("B029 task block not found")
    block = match.group(1).rstrip()
    if "Canonical implementation: PR #149" in block:
        raise SystemExit("B029 canonical implementation already recorded")
    block += (
        "\n  Canonical implementation: PR #149 / final head "
        f"`{FINAL_HEAD}` / merge `{MERGE_SHA}`.\n"
    )
    text = text[: match.start()] + block + text[match.end() :]
    TASKS.write_text(text, encoding="utf-8")


def update_evidence() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    state = "**State:** `IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT`"
    if text.count(state) != 1:
        raise SystemExit("unexpected B029 evidence state")
    text = text.replace(state, "**State:** COMPLETE_CANONICAL", 1)

    task_line = "**Task:** `MSTR-000B / B029`\n"
    if text.count(task_line) != 1:
        raise SystemExit("unexpected B029 task metadata")
    metadata = (
        task_line
        + "**Implementation PR:** #149\n"
        + f"**Final implementation head:** `{FINAL_HEAD}`\n"
        + f"**Canonical implementation merge:** `{MERGE_SHA}`\n"
    )
    text = text.replace(task_line, metadata, 1)
    if "## Canonical Implementation Closeout" in text:
        raise SystemExit("B029 closeout section already exists")

    closeout = f"""

## Canonical Implementation Closeout

B029's adaptive test-time compute and selective-context policy contracts were merged and independently verified on canonical `main`. This closeout records terminal task/provenance state only; it does not change the frozen schemas, schema registration, fixtures, runtime semantics, task prerequisites, or any external-effect authority.

- implementation PR: `#149`
- final implementation head: `{FINAL_HEAD}`
- canonical implementation merge: `{MERGE_SHA}`
- exact entry gate v2: run `33792125789` — SUCCESS
- implementation builder v1: run `33794038421` — FAILED Ruff E501 after full-test pass; preserved negative evidence
- implementation builder v2: run `33794732024` — FAILED final diff-check after full-test/Ruff/mypy/validation pass; preserved negative evidence
- final implementation builder v3: run `33795227237` — SUCCESS
- exact-head qualification: run `33796297573` — SUCCESS
- independent semantic review: run `33796374380` — SUCCESS / FINDINGS=NONE
- mandatory pre-merge verification: run `33796812445` — SUCCESS
- post-merge implementation verification: run `33797367994` — SUCCESS

The frozen policy remains one-attempt-by-default, fail-closed on escalation evidence, bounded by explicit marginal-cost caps, and subordinate to A006 protected finalizer authority. Selective context continues to prohibit implicit retrieval and records unsupported active-contract capabilities explicitly rather than fabricating support.

This closeout grants no model-weight access, model execution, quantization execution, gated-terms acceptance, paid API/compute, large/private/production data ingestion, weight-changing training, large-scale RL, or production release authority. B030 remains independently governed by A007/A008/A009/B024/B025 and may proceed only through its own exact-main eligibility lifecycle. B011 and B013 remain separately blocked by their canonical authority/dependency boundaries.
"""
    EVIDENCE.write_text(text.rstrip() + closeout, encoding="utf-8")


def update_task_tests() -> None:
    text = TASK_TESTS.read_text(encoding="utf-8")
    if "test_b029_is_terminal_after_canonical_closeout" in text:
        raise SystemExit("B029 terminal regression already present")
    terminal_test = '''


def test_b029_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B029", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "A005",
        "A006",
        "A008",
        "A010",
        "B020",
    }
    assert all(
        item["observed_state"] == "COMPLETE_CANONICAL"
        for item in result["prerequisite_results"]
    )
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)
'''
    TASK_TESTS.write_text(text.rstrip() + terminal_test, encoding="utf-8")


def update_convergence_tests() -> None:
    text = CONVERGENCE_TESTS.read_text(encoding="utf-8")
    old = 'assert tasks["B029"]["canonical_state"] == "PENDING"'
    if text.count(old) != 2:
        raise SystemExit(f"unexpected B029 convergence assertions={text.count(old)}")
    text = text.replace(old, 'assert tasks["B029"]["canonical_state"] == "COMPLETE_CANONICAL"')
    CONVERGENCE_TESTS.write_text(text, encoding="utf-8")


def main() -> None:
    update_catalog()
    update_tasks()
    update_evidence()
    update_task_tests()
    update_convergence_tests()


if __name__ == "__main__":
    main()
