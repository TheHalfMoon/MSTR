from __future__ import annotations

import json
import re
from pathlib import Path

CONFIG = Path("configs/task-gate/mstr-000b.json")
TASKS = Path("specs/002-code-model-supremacy-foundation/tasks.md")
EVIDENCE = Path("evidence/mstr-000b/B030-long-horizon-quality.md")
TASK_TESTS = Path("tests/contract/test_task_gate.py")
CONVERGENCE_TESTS = Path("tests/contract/test_convergence_external_bindings.py")

FINAL_HEAD = "00502aba975e4fa1c2780e5cca1c779fc6b64f27"
MERGE_SHA = "986cdfdaa2ddc64458a7681caf174f3a0e434a1f"


def update_catalog() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    node = payload["tasks"]["B030"]
    if node["canonical_state"] != "PENDING":
        raise SystemExit(f"unexpected B030 state: {node['canonical_state']}")
    node["canonical_state"] = "COMPLETE_CANONICAL"
    CONFIG.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_tasks() -> None:
    text = TASKS.read_text(encoding="utf-8")
    marker = "- [ ] **B030 Freeze Repository Health Delta + cross-harness robustness evaluation.**"
    checked = marker.replace("[ ]", "[x]")
    if text.count(marker) != 1:
        raise SystemExit(f"pending B030 marker count={text.count(marker)}")
    text = text.replace(marker, checked, 1)
    text = re.sub(
        rf"({re.escape(checked)})[ \t]+(?=\n)",
        r"\1",
        text,
        count=1,
    )
    pattern = re.compile(
        r"(- \[x\] \*\*B030 Freeze Repository Health Delta \+ cross-harness robustness evaluation\.\*\*.*?)(?=\n- \[[ x]\] \*\*B031)",
        re.S,
    )
    match = pattern.search(text)
    if match is None:
        raise SystemExit("B030 task block not found")
    block = match.group(1).rstrip()
    if "Canonical implementation: PR #151" in block:
        raise SystemExit("B030 canonical implementation already recorded")
    block += (
        "\n  Canonical implementation: PR #151 / final head "
        f"`{FINAL_HEAD}` / merge `{MERGE_SHA}`.\n"
    )
    text = text[: match.start()] + block + text[match.end() :]
    TASKS.write_text(text, encoding="utf-8")


def update_evidence() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    state = "**State:** `PENDING`"
    if text.count(state) != 1:
        raise SystemExit("unexpected B030 evidence state")
    text = text.replace(state, "**State:** COMPLETE_CANONICAL", 1)

    task_line = "**Task:** `B030`\n"
    if text.count(task_line) != 1:
        raise SystemExit("unexpected B030 task metadata")
    metadata = (
        task_line
        + "**Implementation PR:** #151\n"
        + f"**Final implementation head:** `{FINAL_HEAD}`\n"
        + f"**Canonical implementation merge:** `{MERGE_SHA}`\n"
    )
    text = text.replace(task_line, metadata, 1)
    if "## Canonical Implementation Closeout" in text:
        raise SystemExit("B030 closeout section already exists")

    closeout = f"""

## Canonical Implementation Closeout

B030's Repository Health Delta and cross-harness robustness contract was guarded-merged and independently verified on canonical `main`. This closeout records terminal task and provenance state only. It does not alter the frozen runtime/design schema copies, fixtures, metric semantics, task prerequisites, external-effect authority, or any execution surface.

- implementation PR: `#151`
- final implementation head: `{FINAL_HEAD}`
- canonical implementation merge: `{MERGE_SHA}`
- exact entry gate v1: run `33802293071` — FAILED evidence-harness only; no target mutation
- exact entry gate v2: run `33802497478` — SUCCESS
- implementation builder v1: run `33803554898` — FAILED evidence-harness canonical-main invocation; no target mutation
- implementation builder v2: run `33803985697` — FAILED evidence-harness entry check; no target mutation
- implementation builder v3: run `33804203430` — FAILED focused contract suite; no target mutation
- final implementation builder v4: run `33804505403` — SUCCESS
- exact-head qualification v1: run `33805156226` — FAILED `git diff --check` on trailing whitespace; preserved negative evidence and repaired without force-push
- exact-head qualification v2: run `33805424908` — SUCCESS
- independent semantic review: run `33805835057` — SUCCESS / FINDINGS=NONE
- mandatory pre-merge verification v2: run `33806460388` — SUCCESS
- post-merge implementation verification v1: run `33806927351` — FAILED evidence-harness title assertion after merge-topology PASS
- post-merge implementation verification v2: run `33807105329` — SUCCESS

The frozen contract remains multi-round and attribution-preserving across `RAW_MODEL`, `H0`, `H1`, and `H2`. Its eight repository-health dimensions remain explicit, `NO_VERIFIED_COMPLETION` remains scoreless, and any blocking or unresolved harness lock-in, technical-debt accumulation, or cross-harness comparability risk remains fail-closed for comparison claims.

This closeout grants no model-weight access, model execution, harness execution, quantization execution, gated-terms acceptance, paid API/compute, large/private/production data ingestion, weight-changing training, large-scale RL, or production release authority. B031 remains independently gated by A019 and A020 after B030 closes. B011/B012/B013 remain outside B030 authority and retain their canonical access/dependency boundaries.
"""
    EVIDENCE.write_text(text.rstrip() + closeout, encoding="utf-8")


def update_task_tests() -> None:
    text = TASK_TESTS.read_text(encoding="utf-8")
    if "test_b030_is_terminal_after_canonical_closeout" in text:
        raise SystemExit("B030 terminal regression already present")
    terminal_test = '''


def test_b030_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B030", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "A007",
        "A008",
        "A009",
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
'''
    TASK_TESTS.write_text(text.rstrip() + terminal_test, encoding="utf-8")


def update_convergence_tests() -> None:
    text = CONVERGENCE_TESTS.read_text(encoding="utf-8")
    old = 'assert tasks["B030"]["canonical_state"] == "PENDING"'
    if text.count(old) != 2:
        raise SystemExit(f"unexpected B030 convergence assertions={text.count(old)}")
    text = text.replace(old, 'assert tasks["B030"]["canonical_state"] == "COMPLETE_CANONICAL"')
    CONVERGENCE_TESTS.write_text(text, encoding="utf-8")


def main() -> None:
    update_catalog()
    update_tasks()
    update_evidence()
    update_task_tests()
    update_convergence_tests()


if __name__ == "__main__":
    main()
