from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected unique anchor, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "configs/task-gate/mstr-000b.json",
    '    "B020": {\n      "canonical_state": "PENDING",',
    '    "B020": {\n      "canonical_state": "COMPLETE_CANONICAL",',
)

evidence_path = Path("evidence/mstr-000b/B020-difficulty-contract.md")
evidence = evidence_path.read_text(encoding="utf-8")
old_header = (
    "**Task:** `B020`\n"
    "**State:** `IMPLEMENTATION_ACTIVE`\n"
    "**Contract:** `mstr.difficulty-calibration.v0`\n"
)
new_header = (
    "**Task:** `B020`\n"
    "**Implementation PR:** #81\n"
    "**Final implementation head:** `189509470eae10f1080938b0b2b873f375842f35`\n"
    "**Canonical implementation merge:** `f5a4892bff6bc20e376efcaa8f554c15ac88bca8`\n"
    "**State:** COMPLETE_CANONICAL\n"
    "**Contract:** `mstr.difficulty-calibration.v0`\n"
)
if evidence.count(old_header) != 1:
    raise SystemExit("B020 evidence header anchor mismatch")
evidence = evidence.replace(old_header, new_header, 1)
closeout_lines = [
    "",
    "## Canonical Implementation Closeout",
    "",
    "The checkpoint-relative difficulty calibration contract was merged and verified on canonical main without executing a model, calibrating a real checkpoint, or widening any external-effect authority.",
    "",
    "- implementation PR: `#81`",
    "- final implementation head: `189509470eae10f1080938b0b2b873f375842f35`",
    "- canonical implementation merge: `f5a4892bff6bc20e376efcaa8f554c15ac88bca8`",
    "- atomic implementation build: run `33199352285` — SUCCESS",
    "- finite-structural-feature hardening: run `33200021831` — SUCCESS",
    "- exact hardened-head qualification: run `33234320679` — SUCCESS",
    "- independent adversarial review: run `33234412303` — SUCCESS",
    "- mandatory pre-merge verification: run `33234492918` — SUCCESS",
    "- post-merge implementation verification: run `33234636531` — SUCCESS",
    "",
    "This closeout changes only canonical task/provenance state and terminal-behavior regression assertions. It grants no model-weight access, model execution, real calibration execution, teacher/API use, paid compute, network model calls, large/private/production data ingestion, weight-changing training, B021 frontier-sampler execution, large-scale RL, or production release authority. B011 remains blocked.",
]
if "## Canonical Implementation Closeout" in evidence:
    raise SystemExit("B020 closeout section already exists")
evidence_path.write_text(evidence.rstrip() + "\n" + "\n".join(closeout_lines) + "\n", encoding="utf-8")

tasks = Path("specs/002-code-model-supremacy-foundation/tasks.md")
text = tasks.read_text(encoding="utf-8")
old_task = (
    "- [ ] **B020 Freeze checkpoint-relative difficulty calibration contract.**  \n"
    "  Define exact student/harness/sampling identity and classes `TOO_EASY`, `LEARNABLE_FRONTIER`, `HARD_FRONTIER`, `CURRENTLY_UNPRODUCTIVE`, `INVALID`.  \n"
    "  Outputs: schema/fixtures, `evidence/mstr-000b/B020-difficulty-contract.md`.\n"
)
new_task = (
    "- [x] **B020 Freeze checkpoint-relative difficulty calibration contract.**\n"
    "  Define exact student/harness/sampling identity and classes `TOO_EASY`, `LEARNABLE_FRONTIER`, `HARD_FRONTIER`, `CURRENTLY_UNPRODUCTIVE`, `INVALID`.  \n"
    "  Outputs: schema/fixtures, `evidence/mstr-000b/B020-difficulty-contract.md`.\n"
    "  Canonical implementation: PR #81 / final head `189509470eae10f1080938b0b2b873f375842f35` / merge `f5a4892bff6bc20e376efcaa8f554c15ac88bca8`.\n"
)
if text.count(old_task) != 1:
    raise SystemExit("B020 tasks anchor mismatch")
tasks.write_text(text.replace(old_task, new_task, 1), encoding="utf-8")

gate_test = Path("tests/contract/test_task_gate.py")
text = gate_test.read_text(encoding="utf-8")
marker = '@pytest.mark.parametrize("task_id", ["B020", "B022", "B025"])\n'
insertion = '''def test_b020_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B020", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b020_closeout_opens_b021_frontier_sampler() -> None:
    result = evaluate_task_snapshot("B021", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert result["authority_result"]["required"] is False
    predecessor = next(
        item for item in result["prerequisite_results"] if item["task_id"] == "B020"
    )
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", result)


@pytest.mark.parametrize("task_id", ["B022", "B025"])
'''
if text.count(marker) != 1:
    raise SystemExit("B020 task-gate marker mismatch")
gate_test.write_text(text.replace(marker, insertion, 1), encoding="utf-8")

contract_test = Path("tests/contract/test_difficulty_calibration_contract.py")
text = contract_test.read_text(encoding="utf-8")
closeout_test = '''


def test_b020_canonical_closeout_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B020-difficulty-contract.md").read_text(
        encoding="utf-8"
    )
    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #81" in evidence
    assert "`189509470eae10f1080938b0b2b873f375842f35`" in evidence
    assert "`f5a4892bff6bc20e376efcaa8f554c15ac88bca8`" in evidence
    for run_id in (
        "33199352285",
        "33200021831",
        "33234320679",
        "33234412303",
        "33234492918",
        "33234636531",
    ):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B020_CALIBRATION_EXECUTION = NONE" in evidence
    assert "B021_FRONTIER_SAMPLER_EXECUTION = NONE" in evidence
'''
if "def test_b020_canonical_closeout_provenance_and_authority_boundary()" in text:
    raise SystemExit("B020 closeout contract test already exists")
contract_test.write_text(
    (text.rstrip() + closeout_test).rstrip() + "\n",
    encoding="utf-8",
)

cli_test = Path("tests/integration/test_task_gate_cli.py")
text = cli_test.read_text(encoding="utf-8")
cli_closeout = '''


def test_task_eligible_b020_terminal_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = evaluate_task_snapshot("B020", canonical_main=_CANONICAL_MAIN)

    def fake_evaluate_task_eligibility(task_id: str) -> dict[str, object]:
        assert task_id == "B020"
        return expected

    monkeypatch.setattr(
        "mstr_qualify.cli.evaluate_task_eligibility", fake_evaluate_task_eligibility
    )
    exit_code = main(["task", "eligible", "B020"])
    payload = _stdout_json(capsys)
    assert exit_code == 1
    assert payload == expected
    assert payload["eligible"] is False
    assert "task.already_terminal" in payload["reasons"]
    validate_instance("mstr-task-eligibility-v0", payload)
'''
if "def test_task_eligible_b020_terminal_returns_one(" in text:
    raise SystemExit("B020 terminal CLI test already exists")
cli_test.write_text(
    (text.rstrip() + cli_closeout).rstrip() + "\n",
    encoding="utf-8",
)
