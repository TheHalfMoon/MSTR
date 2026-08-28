from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

BASE = Path(sys.argv[1]).resolve()
CANDIDATE = Path(sys.argv[2]).resolve()


def read(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


base = json.loads(read(BASE, "configs/task-gate/mstr-000b.json"))
candidate = json.loads(read(CANDIDATE, "configs/task-gate/mstr-000b.json"))
assert base["catalog_version"] == candidate["catalog_version"]
assert base["defaults"] == candidate["defaults"]
base_tasks = base["tasks"]
candidate_tasks = candidate["tasks"]
assert set(base_tasks) == set(candidate_tasks)

expected = copy.deepcopy(base_tasks["B019"])
assert expected["canonical_state"] == "PENDING"
expected["canonical_state"] = "COMPLETE_CANONICAL"
assert candidate_tasks["B019"] == expected
for task_id in sorted(base_tasks):
    if task_id == "B019":
        continue
    assert candidate_tasks[task_id] == base_tasks[task_id], task_id

for task_id, state in (("B011", "BLOCKED"), ("B020", "PENDING"), ("B022", "PENDING")):
    assert candidate_tasks[task_id]["canonical_state"] == state

ledger = read(CANDIDATE, "specs/002-code-model-supremacy-foundation/tasks.md")
assert "- [x] **B019 Freeze bounded teacher-rescue policy.**" in ledger
assert "- [ ] **B020 Freeze checkpoint-relative difficulty calibration contract.**" in ledger
assert "- [ ] **B022 Freeze `VerifierHealthRecord` contract." in ledger
assert "PR #78 / final head `25907c32fb60e83a6b171192e8c12c8092bc9f5e` / merge `ac68e2ff9de9962807ab32ce983b2e808bf4fab9`" in ledger

evidence = read(CANDIDATE, "evidence/mstr-000b/B019-teacher-policy.md")
for phrase in (
    "**State:** COMPLETE_CANONICAL",
    "**Implementation PR:** #78",
    "`25907c32fb60e83a6b171192e8c12c8092bc9f5e`",
    "`ac68e2ff9de9962807ab32ce983b2e808bf4fab9`",
    "run `33193446438` — SUCCESS",
    "run `33193784736` / job `98925641414` — SUCCESS",
    "run `33193968205` — SUCCESS",
    "run `33194149258` — SUCCESS",
    "MODEL_WEIGHT_ACCESS = NONE",
    "MODEL_EXECUTION = NONE",
    "TEACHER_API_EXECUTION = NONE",
    "PAID_MODEL_API = NONE",
    "PAID_COMPUTE = NONE",
    "NETWORK_TEACHER_CALL = NONE",
    "LARGE_DATASET_INGESTION = NONE",
    "WEIGHT_CHANGING_TRAINING = NONE",
    "PRODUCTION_RELEASE = NONE",
    "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE",
    "B022_VERIFIER_HEALTH_AUTHORITY = NONE",
    "B011 remains blocked",
):
    assert phrase in evidence

tests = read(CANDIDATE, "tests/contract/test_teacher_rescue_contract.py")
assert "test_b019_canonical_closeout_provenance_and_authority_boundary" in tests
task_tests = read(CANDIDATE, "tests/contract/test_task_gate.py")
assert "test_b019_is_terminal_after_canonical_closeout" in task_tests
cli_tests = read(CANDIDATE, "tests/integration/test_task_gate_cli.py")
assert "test_task_eligible_b019_terminal_returns_one" in cli_tests
