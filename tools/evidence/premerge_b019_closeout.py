from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

BASE = Path(sys.argv[1]).resolve()
HEAD = Path(sys.argv[2]).resolve()


def read(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


base_catalog = json.loads(read(BASE, "configs/task-gate/mstr-000b.json"))
head_catalog = json.loads(read(HEAD, "configs/task-gate/mstr-000b.json"))
assert base_catalog["catalog_version"] == head_catalog["catalog_version"]
assert base_catalog["defaults"] == head_catalog["defaults"]
base_tasks = base_catalog["tasks"]
head_tasks = head_catalog["tasks"]
assert set(base_tasks) == set(head_tasks)

expected_b019 = copy.deepcopy(base_tasks["B019"])
assert expected_b019["canonical_state"] == "PENDING"
expected_b019["canonical_state"] = "COMPLETE_CANONICAL"
assert head_tasks["B019"] == expected_b019
for task_id in base_tasks:
    if task_id != "B019":
        assert head_tasks[task_id] == base_tasks[task_id], task_id

assert head_tasks["B011"]["canonical_state"] == "BLOCKED"
assert head_tasks["B020"]["canonical_state"] == "PENDING"
assert head_tasks["B022"]["canonical_state"] == "PENDING"

ledger = read(HEAD, "specs/002-code-model-supremacy-foundation/tasks.md")
assert "- [x] **B019 Freeze bounded teacher-rescue policy.**" in ledger
assert "- [ ] **B020 Freeze checkpoint-relative difficulty calibration contract.**" in ledger

evidence = read(HEAD, "evidence/mstr-000b/B019-teacher-policy.md")
for phrase in (
    "**State:** COMPLETE_CANONICAL",
    "**Implementation PR:** #78",
    "**Final implementation head:** `25907c32fb60e83a6b171192e8c12c8092bc9f5e`",
    "**Canonical implementation merge:** `ac68e2ff9de9962807ab32ce983b2e808bf4fab9`",
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
):
    assert phrase in evidence
