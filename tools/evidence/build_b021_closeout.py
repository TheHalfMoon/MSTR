from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()

CATALOG = ROOT / "configs/task-gate/mstr-000b.json"
TASKS = ROOT / "specs/002-code-model-supremacy-foundation/tasks.md"
EVIDENCE = ROOT / "evidence/mstr-000b/B021-frontier-sampler.md"
FRONTIER_TEST = ROOT / "tests/unit/test_frontier_curriculum.py"
TASK_GATE_TEST = ROOT / "tests/contract/test_task_gate.py"
CLI_TEST = ROOT / "tests/integration/test_task_gate_cli.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"expected one match in {path}: {old!r}; found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
node = catalog["tasks"]["B021"]
if node["canonical_state"] != "PENDING":
    raise SystemExit(f"unexpected B021 state: {node['canonical_state']}")
node["canonical_state"] = "COMPLETE_CANONICAL"
CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

replace_once(
    TASKS,
    "- [ ] **B021 Implement fixture-only frontier sampler/calibrator.**  \n"
    "  Demonstrate refreshable task difficulty and sampling decisions without training or large data. Preserve easier replay/regression anchors and harder frontier cells.  \n"
    "  Outputs: `src/mstr_qualify/curriculum/`, tests, `evidence/mstr-000b/B021-frontier-sampler.md`.\n",
    "- [x] **B021 Implement fixture-only frontier sampler/calibrator.**  \n"
    "  Demonstrate refreshable task difficulty and sampling decisions without training or large data. Preserve easier replay/regression anchors and harder frontier cells.  \n"
    "  Outputs: `src/mstr_qualify/curriculum/`, tests, `evidence/mstr-000b/B021-frontier-sampler.md`.\n"
    "  Canonical implementation: PR #83 / final head `6211a8f2ccf2613f2e988ce230c7d432877b1aff` / merge `613449e0f1b23eaef7dcb702ba2636a157816d26`.\n",
)

replace_once(
    EVIDENCE,
    "**Task:** `B021`\n**State:** `IMPLEMENTATION_ACTIVE`\n**Canonical entry main:** `641e13033b00451ea4b81063640e4066a8c7389d`\n",
    "**Task:** `B021`\n"
    "**Implementation PR:** #83\n"
    "**Final implementation head:** `6211a8f2ccf2613f2e988ce230c7d432877b1aff`\n"
    "**Canonical implementation merge:** `613449e0f1b23eaef7dcb702ba2636a157816d26`\n"
    "**State:** COMPLETE_CANONICAL\n"
    "**Canonical entry main:** `641e13033b00451ea4b81063640e4066a8c7389d`\n",
)

with EVIDENCE.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n## Canonical Implementation Closeout\n\n"
        "The fixture-only frontier sampler/calibrator was merged and verified on canonical main without executing a model, calibrating a real checkpoint, accessing weights, or widening any external-effect authority.\n\n"
        "- implementation PR: `#83`\n"
        "- final implementation head: `6211a8f2ccf2613f2e988ce230c7d432877b1aff`\n"
        "- canonical implementation merge: `613449e0f1b23eaef7dcb702ba2636a157816d26`\n"
        "- atomic implementation build: run `33235980087` — SUCCESS\n"
        "- exact-head qualification: run `33236137441` — SUCCESS\n"
        "- exact-head formal review: review `5057065431` — NO BLOCKING FINDINGS\n"
        "- mandatory pre-merge verification: run `33236949430` — SUCCESS\n"
        "- post-merge implementation verification: run `33237180697` — SUCCESS\n\n"
        "This closeout changes only canonical task/provenance state and terminal-behavior regression assertions. It grants no model-weight access, model execution, real checkpoint calibration, teacher/API use, paid compute, network model calls, large/private/production data ingestion, weight-changing training, large-scale RL, or production release authority. B011 remains blocked.\n"
    )

with FRONTIER_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\ndef test_b021_canonical_closeout_provenance_and_authority_boundary() -> None:\n"
        "    evidence = (ROOT / \"evidence\" / \"mstr-000b\" / \"B021-frontier-sampler.md\").read_text(\n"
        "        encoding=\"utf-8\"\n"
        "    )\n"
        "    assert \"**State:** COMPLETE_CANONICAL\" in evidence\n"
        "    assert \"**Implementation PR:** #83\" in evidence\n"
        "    assert \"`6211a8f2ccf2613f2e988ce230c7d432877b1aff`\" in evidence\n"
        "    assert \"`613449e0f1b23eaef7dcb702ba2636a157816d26`\" in evidence\n"
        "    for run_id in (\"33235980087\", \"33236137441\", \"33236949430\", \"33237180697\"):\n"
        "        assert f\"run `{run_id}` — SUCCESS\" in evidence\n"
        "    assert \"review `5057065431` — NO BLOCKING FINDINGS\" in evidence\n"
        "    assert \"MODEL_WEIGHT_ACCESS = NONE\" in evidence\n"
        "    assert \"MODEL_EXECUTION = NONE\" in evidence\n"
        "    assert \"REAL_CHECKPOINT_CALIBRATION = NONE\" in evidence\n"
        "    assert \"WEIGHT_CHANGING_TRAINING = NONE\" in evidence\n"
    )

with TASK_GATE_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\ndef test_b021_is_terminal_after_canonical_closeout() -> None:\n"
        "    result = evaluate_task_snapshot(\"B021\", canonical_main=_CANONICAL_MAIN)\n\n"
        "    assert result[\"eligible\"] is False\n"
        "    assert result[\"state_consistency_result\"][\"observed_state\"] == \"COMPLETE_CANONICAL\"\n"
        "    assert result[\"state_consistency_result\"][\"satisfied\"] is True\n"
        "    assert result[\"authority_result\"][\"required\"] is False\n"
        "    assert \"task.already_terminal\" in result[\"reasons\"]\n"
        "    validate_instance(\"mstr-task-eligibility-v0\", result)\n\n\n"
        "@pytest.mark.parametrize(\"task_id\", [\"B022\", \"B025\"])\n"
        "def test_b021_closeout_preserves_independent_phase_v_successors(task_id: str) -> None:\n"
        "    result = evaluate_task_snapshot(task_id, canonical_main=_CANONICAL_MAIN)\n\n"
        "    assert result[\"eligible\"] is True\n"
        "    assert result[\"state_consistency_result\"][\"observed_state\"] == \"PENDING\"\n"
        "    assert result[\"authority_result\"][\"required\"] is False\n"
        "    validate_instance(\"mstr-task-eligibility-v0\", result)\n"
    )

with CLI_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\ndef test_task_eligible_b021_terminal_returns_one(\n"
        "    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]\n"
        ") -> None:\n"
        "    expected = evaluate_task_snapshot(\"B021\", canonical_main=_CANONICAL_MAIN)\n\n"
        "    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:\n"
        "        assert task_id == \"B021\"\n"
        "        return expected\n\n"
        "    monkeypatch.setattr(\n"
        "        \"mstr_qualify.cli.evaluate_task_eligibility\", fake_evaluate_task_eligibility\n"
        "    )\n"
        "    exit_code = main([\"task\", \"eligible\", \"B021\"])\n"
        "    payload = _stdout_json(capsys)\n"
        "    assert exit_code == 1\n"
        "    assert payload == expected\n"
        "    assert payload[\"eligible\"] is False\n"
        "    assert \"task.already_terminal\" in payload[\"reasons\"]\n"
        "    validate_instance(\"mstr-task-eligibility-v0\", payload)\n"
    )
