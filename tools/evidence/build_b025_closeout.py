from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
CATALOG = ROOT / "configs/task-gate/mstr-000b.json"
TASKS = ROOT / "specs/002-code-model-supremacy-foundation/tasks.md"
EVIDENCE = ROOT / "evidence/mstr-000b/B025-greenfield-curriculum.md"
CONTRACT_TEST = ROOT / "tests/contract/test_greenfield_task_contract.py"
TASK_GATE_TEST = ROOT / "tests/contract/test_task_gate.py"
CLI_TEST = ROOT / "tests/integration/test_task_gate_cli.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match in {path}: {old!r}; found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
node = catalog["tasks"]["B025"]
if node["canonical_state"] != "PENDING":
    raise SystemExit(f"unexpected B025 state: {node['canonical_state']}")
node["canonical_state"] = "COMPLETE_CANONICAL"
CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

replace_once(
    TASKS,
    "- [ ] **B025 Freeze greenfield/feature/synthesis curriculum.**  \n"
    "  Define G0 function, G1 module+tests, G2 component/file, G3 multi-file feature, G4 bounded program, G5 multi-round evolution. Include feature-tree/semantic synthesis as experimental generator with independent verification.  \n"
    "  Outputs: `docs/data/GREENFIELD_FEATURE_CURRICULUM.md`, task manifest schema/fixtures, `evidence/mstr-000b/B025-greenfield-curriculum.md`.\n",
    "- [x] **B025 Freeze greenfield/feature/synthesis curriculum.**\n"
    "  Define G0 function, G1 module+tests, G2 component/file, G3 multi-file feature, G4 bounded program, G5 multi-round evolution. Include feature-tree/semantic synthesis as experimental generator with independent verification.  \n"
    "  Outputs: `docs/data/GREENFIELD_FEATURE_CURRICULUM.md`, task manifest schema/fixtures, `evidence/mstr-000b/B025-greenfield-curriculum.md`.\n"
    "  Canonical implementation: PR #87 / final head `5d569acd15fdd20a2aea7f0c37e63917e73aa54c` / merge `7da90d2d9cb16a8ebd6c5ede390139831370e861`.\n",
)

replace_once(
    EVIDENCE,
    "**Task:** `B025`\n**State:** `IMPLEMENTATION_ACTIVE`\n**Canonical entry main:** `cd3e3ba39c0e83548748275d08b7a3d0d2e6b15b`\n",
    "**Task:** `B025`\n"
    "**Implementation PR:** #87\n"
    "**Final implementation head:** `5d569acd15fdd20a2aea7f0c37e63917e73aa54c`\n"
    "**Canonical implementation merge:** `7da90d2d9cb16a8ebd6c5ede390139831370e861`\n"
    "**State:** COMPLETE_CANONICAL\n"
    "**Canonical entry main:** `cd3e3ba39c0e83548748275d08b7a3d0d2e6b15b`\n",
)

with EVIDENCE.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n## Canonical Implementation Closeout\n\n"
        "The B025 greenfield/feature/synthesis curriculum contract was merged and verified on canonical main without executing synthesis, executing a model, accessing model weights, ingesting an external dataset, or performing weight-changing training. Independent exact-head review found one internal provenance-binding defect before merge; the defect was repaired, requalified, and independently re-reviewed before the mandatory pre-merge gate.\n\n"
        "- implementation PR: `#87`\n"
        "- initial implementation head: `a5d42bb51957c478e9f525c8d0ac0dccc50d32da`\n"
        "- final implementation head: `5d569acd15fdd20a2aea7f0c37e63917e73aa54c`\n"
        "- canonical implementation merge: `7da90d2d9cb16a8ebd6c5ede390139831370e861`\n"
        "- atomic implementation build: run `33247628800` — SUCCESS\n"
        "- initial exact-head qualification: run `33247746466` — SUCCESS\n"
        "- initial exact-head review: review `5057715205` — BLOCKING FINDING RECORDED\n"
        "- fail-closed generator-kind repair: run `33247929504` — SUCCESS\n"
        "- repaired exact-head qualification: run `33248051276` — SUCCESS\n"
        "- repaired exact-head review: review `5057744406` — NO BLOCKING FINDINGS\n"
        "- mandatory pre-merge verification: run `33248243627` — SUCCESS\n"
        "- post-merge implementation verification: run `33248331741` — SUCCESS\n\n"
        "The repaired frozen contract binds `FEATURE_TREE_SYNTHESIS` to `FEATURE_TREE` generator evidence and `SEMANTIC_SYNTHESIS` to `SEMANTIC_COMPLEXITY` generator evidence. Cross-kind evidence fails closed. This closeout changes only canonical task/provenance state and terminal-behavior regression assertions. It does not change the frozen greenfield-task schema, schema fixtures, schema registration, or CLI schema surface. It grants no synthesis execution, model execution, model-weight access, verifier-health evaluator execution, teacher/API use, paid compute, network model calls, large/private/production data ingestion, weight-changing training, large-scale RL, or production release authority. B011 remains blocked by repository-specific external authority.\n"
    )

replace_once(
    TASK_GATE_TEST,
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
    "def test_b014_closeout_preserves_b028_direct_nongated_successor() -> None:\n"
    '    result = evaluate_task_snapshot("B028", canonical_main=_CANONICAL_MAIN)\n\n'
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
    "def test_b021_closeout_preserves_b025_independent_successor() -> None:\n"
    '    result = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    assert result["authority_result"]["required"] is False\n'
    '    validate_instance("mstr-task-eligibility-v0", result)\n',
    "def test_b021_closeout_preserves_b028_independent_successor() -> None:\n"
    '    result = evaluate_task_snapshot("B028", canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    assert result["authority_result"]["required"] is False\n'
    '    validate_instance("mstr-task-eligibility-v0", result)\n',
)

replace_once(
    TASK_GATE_TEST,
    "def test_b022_closeout_preserves_b025_as_next_machine_eligible_task() -> None:\n"
    '    result = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["reasons"] == []\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    validate_instance("mstr-task-eligibility-v0", result)',
    "def test_b022_closeout_preserves_b028_as_machine_eligible_task() -> None:\n"
    '    result = evaluate_task_snapshot("B028", canonical_main=_CANONICAL_MAIN)\n\n'
    '    assert result["eligible"] is True\n'
    '    assert result["reasons"] == []\n'
    '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
    '    predecessor = next(\n'
    '        item for item in result["prerequisite_results"] if item["task_id"] == "B022"\n'
    '    )\n'
    '    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"\n'
    '    assert predecessor["satisfied"] is True\n'
    '    validate_instance("mstr-task-eligibility-v0", result)',
)

with TASK_GATE_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\n\ndef test_b025_is_terminal_after_canonical_closeout() -> None:\n"
        '    result = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)\n\n'
        '    assert result["eligible"] is False\n'
        '    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"\n'
        '    assert result["state_consistency_result"]["satisfied"] is True\n'
        '    assert result["authority_result"]["required"] is False\n'
        '    assert "task.already_terminal" in result["reasons"]\n'
        '    predecessor = next(\n'
        '        item for item in result["prerequisite_results"] if item["task_id"] == "B014"\n'
        '    )\n'
        '    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"\n'
        '    assert predecessor["satisfied"] is True\n'
        '    validate_instance("mstr-task-eligibility-v0", result)\n\n\n'
        "def test_b025_closeout_satisfies_only_its_b026_prerequisite() -> None:\n"
        '    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)\n\n'
        '    assert result["eligible"] is False\n'
        '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
        '    assert "prerequisite.unsatisfied:B025" not in result["reasons"]\n'
        '    assert "prerequisite.unsatisfied:B024" in result["reasons"]\n'
        '    predecessor = next(\n'
        '        item for item in result["prerequisite_results"] if item["task_id"] == "B025"\n'
        '    )\n'
        '    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"\n'
        '    assert predecessor["evidence_present"] is True\n'
        '    assert predecessor["satisfied"] is True\n'
        '    validate_instance("mstr-task-eligibility-v0", result)\n\n\n'
        "def test_b025_closeout_preserves_b028_machine_eligibility() -> None:\n"
        '    result = evaluate_task_snapshot("B028", canonical_main=_CANONICAL_MAIN)\n\n'
        '    assert result["eligible"] is True\n'
        '    assert result["reasons"] == []\n'
        '    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n'
        '    validate_instance("mstr-task-eligibility-v0", result)\n'
    )

with CLI_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\n\ndef test_task_eligible_b025_terminal_returns_one(\n"
        "    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]\n"
        ") -> None:\n"
        '    expected = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)\n\n'
        "    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:\n"
        '        assert task_id == "B025"\n'
        "        return expected\n\n"
        "    monkeypatch.setattr(\n"
        '        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility\n'
        "    )\n"
        '    exit_code = main(["task", "eligible", "B025"])\n'
        "    payload = _stdout_json(capsys)\n"
        "    assert exit_code == 1\n"
        "    assert payload == expected\n"
        '    assert payload["eligible"] is False\n'
        '    assert "task.already_terminal" in payload["reasons"]\n'
        '    validate_instance("mstr-task-eligibility-v0", payload)\n'
    )

with CONTRACT_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\n\ndef test_b025_canonical_closeout_provenance_and_authority_boundary() -> None:\n"
        '    evidence = (ROOT / "evidence" / "mstr-000b" / "B025-greenfield-curriculum.md").read_text(\n'
        '        encoding="utf-8"\n'
        "    )\n"
        '    assert "**State:** COMPLETE_CANONICAL" in evidence\n'
        '    assert "**Implementation PR:** #87" in evidence\n'
        '    assert "`5d569acd15fdd20a2aea7f0c37e63917e73aa54c`" in evidence\n'
        '    assert "`7da90d2d9cb16a8ebd6c5ede390139831370e861`" in evidence\n'
        '    for run_id in (\n'
        '        "33247628800",\n'
        '        "33247746466",\n'
        '        "33247929504",\n'
        '        "33248051276",\n'
        '        "33248243627",\n'
        '        "33248331741",\n'
        '    ):\n'
        '        assert f"run `{run_id}` — SUCCESS" in evidence\n'
        '    assert "review `5057715205` — BLOCKING FINDING RECORDED" in evidence\n'
        '    assert "review `5057744406` — NO BLOCKING FINDINGS" in evidence\n'
        '    assert "SYNTHESIS_EXECUTION = NONE" in evidence\n'
        '    assert "MODEL_EXECUTION = NONE" in evidence\n'
        '    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence\n'
        '    assert "B025_AUTHORITY = GREENFIELD_FEATURE_CURRICULUM_CONTRACT_AND_FIXTURES_ONLY" in evidence\n'
    )
