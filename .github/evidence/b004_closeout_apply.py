from __future__ import annotations

import json
import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} match count: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: b004_closeout_apply.py <repo-root>")
    root = Path(sys.argv[1]).resolve()

    catalog_path = root / "configs/task-gate/mstr-000b.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog["tasks"]["B004"]["canonical_state"] != "PENDING":
        raise SystemExit("B004 catalog state is not PENDING")
    catalog["tasks"]["B004"]["canonical_state"] = "COMPLETE_CANONICAL"
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    tasks_path = root / "specs/002-code-model-supremacy-foundation/tasks.md"
    old_task = (
        "- [ ] **B004 Reconcile MSTR-000A entry semantics to live reality.**  \n"
        "  Prerequisite: B003 `COMPLETE_CANONICAL` and exact-main `eligible=true`. Mark canonical A001/A002/A003 accurately, including PR #38 head `41122ae8dee65b2a6b3c6b188cf335d74088b06f` and merge `2c02eb68a32264c86f69eb7ffc1c99ad87328376`; preserve A004+ live state; replace the blanket post-T034 entry rule with explicit `EARLY_SAFE` vs `CONVERGENCE` prerequisites. Do not rewrite history or claim incomplete work complete.  \n"
        "  Outputs: canonical task/state/roadmap amendments, `evidence/mstr-000b/B004-000a-sequence-reconciliation.md`."
    )
    new_task = (
        "- [x] **B004 Reconcile MSTR-000A entry semantics to live reality.**\n"
        "  Prerequisite: B003 `COMPLETE_CANONICAL` and exact-main `eligible=true`. Mark canonical A001/A002/A003 accurately, including PR #38 head `41122ae8dee65b2a6b3c6b188cf335d74088b06f` and merge `2c02eb68a32264c86f69eb7ffc1c99ad87328376`; preserve A004+ live state; replace the blanket post-T034 entry rule with explicit `EARLY_SAFE` vs `CONVERGENCE` prerequisites. Do not rewrite history or claim incomplete work complete.\n"
        "  Outputs: canonical task/state/roadmap amendments, `evidence/mstr-000b/B004-000a-sequence-reconciliation.md`.\n"
        "  Canonical implementation: PR #52 / final head `9b8ad22e59e096409b753a6264e61ee59a966dc4` / merge `fa90726a6415cab0b655acae4768c7343cc6370c`."
    )
    replace_once(tasks_path, old_task, new_task, "B004 task closeout")

    evidence_path = root / "evidence/mstr-000b/B004-000a-sequence-reconciliation.md"
    replace_once(
        evidence_path,
        "**State:** IMPLEMENTATION_ACTIVE\n**Entry canonical main:** `d0e90740924f6991da361536e7f835eb55ae9145`",
        "**State:** COMPLETE_CANONICAL\n"
        "**Implementation PR:** `#52`\n"
        "**Final implementation head:** `9b8ad22e59e096409b753a6264e61ee59a966dc4`\n"
        "**Canonical implementation merge:** `fa90726a6415cab0b655acae4768c7343cc6370c`\n"
        "**Entry canonical main:** `d0e90740924f6991da361536e7f835eb55ae9145`\n\n"
        "```text\n"
        "ENTRY_GATE_TASK = B004\n"
        "ENTRY_GATE_CANONICAL_MAIN = d0e90740924f6991da361536e7f835eb55ae9145\n"
        "ENTRY_GATE_ELIGIBLE = true\n"
        "ENTRY_GATE_RUN = 33095418967\n"
        "ENTRY_GATE_JOB = 98598942120\n"
        "```",
        "B004 machine-readable closeout metadata",
    )

    evidence = evidence_path.read_text(encoding="utf-8")
    old_closeout = (
        "## Closeout rule\n\n"
        "B004 remains `IMPLEMENTATION_ACTIVE` until this exact implementation head is independently qualified and reviewed, merged with an expected-head guard, and post-merge canonical main is verified. A separate closeout must then align the MSTR-000B B004 task checkbox/catalog/evidence state. B005 or any other successor work must use its own exact eligibility gate and authority boundary; B004 grants none by implication.\n"
    )
    new_closeout = """## Canonical implementation and closeout evidence

```text
IMPLEMENTATION_PR = #52
FINAL_IMPLEMENTATION_HEAD = 9b8ad22e59e096409b753a6264e61ee59a966dc4
IMPLEMENTATION_MERGE = fa90726a6415cab0b655acae4768c7343cc6370c
FINAL_EXACT_HEAD_QUALIFICATION_RUN = 33096742489
FINAL_EXACT_HEAD_QUALIFICATION_JOB = 98603517596
FINAL_REVIEW = QODO_NO_MATERIAL_ISSUES
POST_MERGE_VERIFICATION_RUN = 33097244928
POST_MERGE_VERIFICATION_JOB = 98605255855
POST_MERGE_B004_ELIGIBLE = true / pre-closeout expected
POST_MERGE_CANONICAL_DRIFT = clean
POST_MERGE_PYTEST = 498 passed
POST_MERGE_RUFF = PASS
POST_MERGE_MYPY = PASS / 26 source files
POST_MERGE_VALIDATE = PASS / 10 valid / 10 invalid rejected
STATE = COMPLETE_CANONICAL
```

The `COMPLETE_CANONICAL` markers in this branch are prospective closeout state only. They become canonical only when the exact qualified and reviewed closeout head is merged to `main` with an expected-head guard. Immediately afterward, post-closeout verification must prove production B004 terminal, production B005 `eligible=true`, canonical drift clean, and all frozen repository gates green before B004 completion is claimed or any B005 material mutation begins.

This transition grants no model-weight, tokenizer, inference, training, paid-compute, or dataset authority. B005 remains subject to its own exact-main `eligible=true` gate and its explicit `No weight access` boundary.
"""
    if old_closeout not in evidence:
        raise SystemExit("B004 closeout rule block not found")
    evidence_path.write_text(evidence.replace(old_closeout, new_closeout, 1), encoding="utf-8")

    contract_path = root / "tests/contract/test_task_gate.py"
    old_contract = '''def test_b004_is_eligible_after_b003_closeout_is_canonical() -> None:\n    result = evaluate_task_snapshot("B004", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is True\n    assert result["prerequisite_results"][0]["task_id"] == "B003"\n    assert result["prerequisite_results"][0]["observed_state"] == "COMPLETE_CANONICAL"\n    assert result["prerequisite_results"][0]["satisfied"] is True\n    assert result["reasons"] == []\n    validate_instance("mstr-task-eligibility-v0", result)\n'''
    new_contract = '''def test_b004_is_terminal_after_canonical_closeout() -> None:\n    result = evaluate_task_snapshot("B004", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is False\n    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"\n    assert result["state_consistency_result"]["satisfied"] is True\n    assert "task.already_terminal" in result["reasons"]\n    validate_instance("mstr-task-eligibility-v0", result)\n\n\ndef test_b005_is_eligible_after_b004_closeout() -> None:\n    result = evaluate_task_snapshot("B005", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is True\n    assert result["prerequisite_results"] == []\n    assert result["reasons"] == []\n    validate_instance("mstr-task-eligibility-v0", result)\n'''
    replace_once(contract_path, old_contract, new_contract, "B004/B005 contract transition")

    integration_path = root / "tests/integration/test_task_gate_cli.py"
    old_integration = '''def test_task_eligible_b004_successor_returns_zero(\n    monkeypatch: pytest.MonkeyPatch,\n    capsys: pytest.CaptureFixture[str],\n) -> None:\n    expected = evaluate_task_snapshot("B004", canonical_main=_CANONICAL_MAIN)\n    monkeypatch.setattr(\n        "mstr_qualify.cli.evaluate_task_eligibility",\n        lambda task_id: expected,\n    )\n\n    exit_code = main(["task", "eligible", "B004"])\n    payload = _stdout_json(capsys)\n\n    assert exit_code == 0\n    assert payload == expected\n    assert payload["eligible"] is True\n    assert payload["reasons"] == []\n    validate_instance("mstr-task-eligibility-v0", payload)\n'''
    new_integration = '''def test_task_eligible_b004_terminal_returns_one(\n    monkeypatch: pytest.MonkeyPatch,\n    capsys: pytest.CaptureFixture[str],\n) -> None:\n    expected = evaluate_task_snapshot("B004", canonical_main=_CANONICAL_MAIN)\n    monkeypatch.setattr(\n        "mstr_qualify.cli.evaluate_task_eligibility",\n        lambda task_id: expected,\n    )\n\n    exit_code = main(["task", "eligible", "B004"])\n    payload = _stdout_json(capsys)\n\n    assert exit_code == 1\n    assert payload == expected\n    assert payload["eligible"] is False\n    assert "task.already_terminal" in payload["reasons"]\n    validate_instance("mstr-task-eligibility-v0", payload)\n\n\ndef test_task_eligible_b005_successor_returns_zero(\n    monkeypatch: pytest.MonkeyPatch,\n    capsys: pytest.CaptureFixture[str],\n) -> None:\n    expected = evaluate_task_snapshot("B005", canonical_main=_CANONICAL_MAIN)\n    monkeypatch.setattr(\n        "mstr_qualify.cli.evaluate_task_eligibility",\n        lambda task_id: expected,\n    )\n\n    exit_code = main(["task", "eligible", "B005"])\n    payload = _stdout_json(capsys)\n\n    assert exit_code == 0\n    assert payload == expected\n    assert payload["eligible"] is True\n    assert payload["reasons"] == []\n    validate_instance("mstr-task-eligibility-v0", payload)\n'''
    replace_once(integration_path, old_integration, new_integration, "B004/B005 CLI transition")


if __name__ == "__main__":
    main()
