from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
CATALOG = ROOT / "configs/task-gate/mstr-000b.json"
TASKS = ROOT / "specs/002-code-model-supremacy-foundation/tasks.md"
EVIDENCE = ROOT / "evidence/mstr-000b/B022-verifier-health.md"
CONTRACT_TEST = ROOT / "tests/contract/test_verifier_health_contract.py"
TASK_GATE_TEST = ROOT / "tests/contract/test_task_gate.py"
CLI_TEST = ROOT / "tests/integration/test_task_gate_cli.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match in {path}: {old!r}; found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
node = catalog["tasks"]["B022"]
if node["canonical_state"] != "PENDING":
    raise SystemExit(f"unexpected B022 state: {node['canonical_state']}")
node["canonical_state"] = "COMPLETE_CANONICAL"
CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

replace_once(
    TASKS,
    "- [ ] **B022 Freeze `VerifierHealthRecord` contract.**  \n"
    "  Require evaluator hashes, protected paths, oracle/no-op/known-bad behavior where applicable, mutation/shortcut tests, generated-test independence, leakage/disagreement signals, and health class.  \n"
    "  Outputs: schema/fixtures, `evidence/mstr-000b/B022-verifier-health.md`.\n",
    "- [x] **B022 Freeze `VerifierHealthRecord` contract.**\n"
    "  Require evaluator hashes, protected paths, oracle/no-op/known-bad behavior where applicable, mutation/shortcut tests, generated-test independence, leakage/disagreement signals, and health class.  \n"
    "  Outputs: schema/fixtures, `evidence/mstr-000b/B022-verifier-health.md`.\n"
    "  Canonical implementation: PR #85 / final head `ab3330afdef9c9329b1d2bb2a7e5aab09064f62b` / merge `97bf66a98bad51ff0d574d90a04fa47b802708ee`.\n",
)

replace_once(
    EVIDENCE,
    "**Task:** `B022`\n**State:** `IMPLEMENTATION_ACTIVE`\n**Canonical entry main:** `127fd5fd1a5a6f1843f207a0272664ae8cb129f4`\n",
    "**Task:** `B022`\n"
    "**Implementation PR:** #85\n"
    "**Final implementation head:** `ab3330afdef9c9329b1d2bb2a7e5aab09064f62b`\n"
    "**Canonical implementation merge:** `97bf66a98bad51ff0d574d90a04fa47b802708ee`\n"
    "**State:** COMPLETE_CANONICAL\n"
    "**Canonical entry main:** `127fd5fd1a5a6f1843f207a0272664ae8cb129f4`\n",
)

with EVIDENCE.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n## Canonical Implementation Closeout\n\n"
        "The B022 verifier-health record contract was merged and verified on canonical main without executing a real verifier, implementing the B023 classifier, accessing model weights, or widening training/external-effect authority.\n\n"
        "- implementation PR: `#85`\n"
        "- final implementation head: `ab3330afdef9c9329b1d2bb2a7e5aab09064f62b`\n"
        "- canonical implementation merge: `97bf66a98bad51ff0d574d90a04fa47b802708ee`\n"
        "- atomic implementation build: run `33245760496` — SUCCESS\n"
        "- exact-head qualification: run `33245884971` — SUCCESS\n"
        "- exact-head formal review: review `5057533717` — NO BLOCKING FINDINGS\n"
        "- mandatory pre-merge verification: run `33245974810` — SUCCESS\n"
        "- post-merge implementation verification: run `33246110168` — SUCCESS\n\n"
        "This closeout changes only canonical task/provenance state and terminal-behavior regression assertions. It does not change the frozen verifier-health schema, fixtures, or schema registration. It grants no real verifier execution, B023 evaluator/classifier authority, test-generation curriculum authority, model execution, model-weight access, training, teacher/API use, paid compute, network model calls, large/private/production data ingestion, large-scale RL, or production release authority. B011 remains blocked.\n"
    )

replace_once(
    TASK_GATE_TEST,
    '@pytest.mark.parametrize("task_id", ["B022", "B025"])\n'
    "def test_b014_closeout_opens_direct_nongated_successors(task_id: str) -> None:\n"
    '    result = evaluate_task_snapshot(task_id, canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["reasons"] == []\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    assert result["authority_result"]["required"] is False\n'
    '    assert result["authority_result"]["satisfied"] is True\n'
    '    predecessor = next(\n'
    '        item for item in result["prerequisite_results"] if item["task_id"] == "B014"\n'
    '    )\n'
    '    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"\n'
    '    assert predecessor["evidence_present"] is True\n'
    '    assert predecessor["satisfied"] is True\n'
    '    assert predecessor["reasons"] == []\n'
    '    validate_instance("mstr-task-eligibility-v0", result)\n',
    "def test_b014_closeout_preserves_b025_direct_nongated_successor() -> None:\n"
    '    result = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["reasons"] == []\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    assert result["authority_result"]["required"] is False\n'
    '    assert result["authority_result"]["satisfied"] is True\n'
    '    predecessor = next(\n'
    '        item for item in result["prerequisite_results"] if item["task_id"] == "B014"\n'
    '    )\n'
    '    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"\n'
    '    assert predecessor["evidence_present"] is True\n'
    '    assert predecessor["satisfied"] is True\n'
    '    assert predecessor["reasons"] == []\n'
    '    validate_instance("mstr-task-eligibility-v0", result)\n',
)

replace_once(
    TASK_GATE_TEST,
    '@pytest.mark.parametrize("task_id", ["B022", "B025"])\n'
    "def test_b021_closeout_preserves_independent_phase_v_successors(task_id: str) -> None:\n"
    '    result = evaluate_task_snapshot(task_id, canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    assert result["authority_result"]["required"] is False\n'
    '    validate_instance("mstr-task-eligibility-v0", result)\n',
    "def test_b021_closeout_preserves_b025_independent_successor() -> None:\n"
    '    result = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    assert result["authority_result"]["required"] is False\n'
    '    validate_instance("mstr-task-eligibility-v0", result)\n',
)

with TASK_GATE_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\ndef test_b022_is_terminal_after_canonical_closeout() -> None:\n"
        '    result = evaluate_task_snapshot("B022", canonical_main=_CANONICAL_MAIN)\n\n'
        '    assert result["eligible"] is False\n'
        '    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"\n'
        '    assert result["state_consistency_result"]["satisfied"] is True\n'
        '    assert result["authority_result"]["required"] is False\n'
        '    assert "task.already_terminal" in result["reasons"]\n'
        '    validate_instance("mstr-task-eligibility-v0", result)\n\n\n'
        "def test_b022_closeout_satisfies_only_its_b023_prerequisite() -> None:\n"
        '    result = evaluate_task_snapshot("B023", canonical_main=_CANONICAL_MAIN)\n\n'
        '    assert result["eligible"] is False\n'
        '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
        '    assert "prerequisite.unsatisfied:B022" not in result["reasons"]\n'
        '    assert "prerequisite.unsatisfied:A006" in result["reasons"]\n'
        '    assert "prerequisite.unsatisfied:A014" in result["reasons"]\n'
        '    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B022")\n'
        '    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"\n'
        '    assert predecessor["evidence_present"] is True\n'
        '    assert predecessor["satisfied"] is True\n'
        '    validate_instance("mstr-task-eligibility-v0", result)\n\n\n'
        "def test_b022_closeout_preserves_b025_as_next_machine_eligible_task() -> None:\n"
        '    result = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)\n\n'
        '    assert result["eligible"] is True\n'
        '    assert result["reasons"] == []\n'
        '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
        '    validate_instance("mstr-task-eligibility-v0", result)\n'
    )

with CLI_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\ndef test_task_eligible_b022_terminal_returns_one(\n"
        "    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]\n"
        ") -> None:\n"
        '    expected = evaluate_task_snapshot("B022", canonical_main=_CANONICAL_MAIN)\n\n'
        "    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:\n"
        '        assert task_id == "B022"\n'
        "        return expected\n\n"
        "    monkeypatch.setattr(\n"
        '        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility\n'
        "    )\n"
        '    exit_code = main(["task", "eligible", "B022"])\n'
        "    payload = _stdout_json(capsys)\n"
        "    assert exit_code == 1\n"
        "    assert payload == expected\n"
        '    assert payload["eligible"] is False\n'
        '    assert "task.already_terminal" in payload["reasons"]\n'
        '    validate_instance("mstr-task-eligibility-v0", payload)\n'
    )

with CONTRACT_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\ndef test_b022_canonical_closeout_provenance_and_authority_boundary() -> None:\n"
        '    evidence = (ROOT / "evidence" / "mstr-000b" / "B022-verifier-health.md").read_text(\n'
        '        encoding="utf-8"\n'
        "    )\n"
        '    assert "**State:** COMPLETE_CANONICAL" in evidence\n'
        '    assert "**Implementation PR:** #85" in evidence\n'
        '    assert "`ab3330afdef9c9329b1d2bb2a7e5aab09064f62b`" in evidence\n'
        '    assert "`97bf66a98bad51ff0d574d90a04fa47b802708ee`" in evidence\n'
        '    for run_id in ("33245760496", "33245884971", "33245974810", "33246110168"):\n'
        '        assert f"run `{run_id}` — SUCCESS" in evidence\n'
        '    assert "review `5057533717` — NO BLOCKING FINDINGS" in evidence\n'
        '    assert "VERIFIER_EVALUATOR_EXECUTION = NONE" in evidence\n'
        '    assert "B023_VERIFIER_HEALTH_EVALUATOR_AUTHORITY = NONE" in evidence\n'
        '    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence\n'
    )
