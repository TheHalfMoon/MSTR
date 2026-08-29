from __future__ import annotations

import json
import re
from pathlib import Path

CONFIG = Path("configs/task-gate/mstr-000b.json")
TASKS = Path("specs/002-code-model-supremacy-foundation/tasks.md")
EVIDENCE = Path("evidence/mstr-000b/B028-training-methods.md")
TESTS = Path("tests/contract/test_task_gate.py")

INITIAL_HEAD = "93f923fecc07b08f4d5f198bfb09209e169957a7"
FINAL_HEAD = "3c9d8624745ad34e1e96d7f150afaccd2f02bc8f"
MERGE_SHA = "01a070e27098fc3798a87ad57dd62b63fdf8fdee"


def update_catalog() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    node = payload["tasks"]["B028"]
    if node["canonical_state"] != "PENDING":
        raise SystemExit(f"unexpected B028 state: {node['canonical_state']}")
    node["canonical_state"] = "COMPLETE_CANONICAL"
    CONFIG.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_tasks() -> None:
    text = TASKS.read_text(encoding="utf-8")
    marker = "- [ ] **B028 Freeze Q4-in-the-loop promotion contract and training-method tournament preflight.**"
    checked_marker = marker.replace("[ ]", "[x]")
    if text.count(marker) != 1:
        raise SystemExit("expected exactly one pending B028 marker")
    text = text.replace(marker, checked_marker, 1)
    text, cleaned = re.subn(
        rf"({re.escape(checked_marker)})[ \t]+(?=\n)",
        r"\1",
        text,
        count=1,
    )
    if cleaned != 1:
        raise SystemExit("expected to normalize B028 task-line trailing whitespace")

    pattern = re.compile(
        r"(- \[x\] \*\*B028 Freeze Q4-in-the-loop promotion contract and training-method tournament preflight\.\*\*.*?)(?=\n- \[[ x]\] \*\*B029)",
        re.S,
    )
    match = pattern.search(text)
    if match is None:
        raise SystemExit("B028 task block not found")
    block = match.group(1).rstrip()
    if "Canonical implementation: PR #90" in block:
        raise SystemExit("B028 canonical implementation already recorded")
    block += (
        "\n  Canonical implementation: PR #90 / final head "
        f"`{FINAL_HEAD}` / merge `{MERGE_SHA}`.\n"
    )
    text = text[: match.start()] + block + text[match.end() :]
    TASKS.write_text(text, encoding="utf-8")


def update_evidence() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    state = "**State:** `IMPLEMENTATION_ACTIVE`"
    if text.count(state) != 1:
        raise SystemExit("unexpected B028 evidence state")
    text = text.replace(state, "**State:** COMPLETE_CANONICAL", 1)

    task_line = "**Task:** `B028`\n"
    if text.count(task_line) != 1:
        raise SystemExit("unexpected B028 task metadata marker")
    metadata = (
        "**Task:** `B028`\n"
        "**Implementation PR:** #90\n"
        f"**Initial implementation head:** `{INITIAL_HEAD}`\n"
        f"**Final implementation head:** `{FINAL_HEAD}`\n"
        f"**Canonical implementation merge:** `{MERGE_SHA}`\n"
    )
    text = text.replace(task_line, metadata, 1)

    old_tail = (
        "B028 is not `COMPLETE_CANONICAL` at implementation time. Canonical completion "
        "requires the normal exact-head review/merge and separate closeout lifecycle."
    )
    if text.count(old_tail) != 1:
        raise SystemExit("B028 implementation-active closeout marker not found")
    closeout = f"""## Canonical Implementation Closeout

B028's Q4 promotion and training-method tournament preflight is canonically implemented by PR #90. The implementation remained contract/preflight-only throughout the lifecycle and did not execute training, inference, quantization, model-weight access, paid compute, dataset ingestion, or production release.

- implementation PR: `#90`
- initial implementation head: `{INITIAL_HEAD}`
- final implementation head: `{FINAL_HEAD}`
- canonical implementation merge: `{MERGE_SHA}`
- atomic implementation builder: run `33251352118` — SUCCESS
- initial exact-head qualification: run `33251458699` — FAILED evidence assertion; not merge-admissible
- initial exact-head review: review `5058031414` — BLOCKING FINDING RECORDED
- fail-closed unsupported-status repair: run `33251566205` — SUCCESS
- repaired exact-head qualification: run `33251670229` — SUCCESS
- repaired exact-head review: review `5058039887` — NO BLOCKING FINDINGS
- mandatory pre-merge verification: run `33251763802` — SUCCESS
- post-merge verification v1: run `33254316346` — FAILED evidence checkout/ref setup after focused/full quality passed; not canonical proof
- post-merge verification v2: run `33254415417` — SUCCESS

The repaired contract requires `status=UNSUPPORTED` to bind `support_status=UNSUPPORTED`, which in turn requires an exact unsupported reason and support-evidence identity. Generic framework guidance remains insufficient candidate-specific support evidence. All four frozen tournament arms remain `REVALIDATION_REQUIRED` in the preflight manifest, `method_selection=UNSELECTED`, and `execution_status=NOT_EXECUTED`.

This closeout changes only canonical task/provenance state plus terminal-behavior regression assertions. It does not modify the B028 schemas, fixtures, registry wiring, Q4 promotion contract, method-tournament preflight manifest, or runtime semantics, and it grants no external-effect authority.
"""
    text = text.replace(old_tail, closeout.rstrip(), 1)
    EVIDENCE.write_text(text.rstrip() + "\n", encoding="utf-8")


def remove_function(text: str, name: str) -> str:
    pattern = re.compile(
        rf"\n\ndef {re.escape(name)}\(\) -> None:.*?(?=\n\ndef |\Z)",
        re.S,
    )
    text, count = pattern.subn("", text, count=1)
    if count != 1:
        raise SystemExit(f"failed to remove obsolete test: {name}")
    return text


def update_tests() -> None:
    text = TESTS.read_text(encoding="utf-8")
    obsolete = [
        "test_b014_closeout_preserves_b028_direct_nongated_successor",
        "test_b021_closeout_preserves_b028_independent_successor",
        "test_b022_closeout_preserves_b028_as_machine_eligible_task",
        "test_b025_closeout_preserves_b028_machine_eligibility",
    ]
    for name in obsolete:
        text = remove_function(text, name)

    terminal_test = '''


def test_b028_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B028", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "B009",
        "B014",
        "B022",
    }
    assert all(
        item["observed_state"] == "COMPLETE_CANONICAL"
        for item in result["prerequisite_results"]
    )
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)
'''
    if "test_b028_is_terminal_after_canonical_closeout" in text:
        raise SystemExit("B028 terminal regression already present")
    TESTS.write_text(text.rstrip() + terminal_test, encoding="utf-8")


def main() -> None:
    update_catalog()
    update_tasks()
    update_evidence()
    update_tests()


if __name__ == "__main__":
    main()
