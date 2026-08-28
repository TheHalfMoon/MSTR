from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

BASE = Path(sys.argv[1]).resolve()
CANDIDATE = Path(sys.argv[2]).resolve()


def read(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


base_catalog = json.loads(read(BASE, "configs/task-gate/mstr-000b.json"))
candidate_catalog = json.loads(read(CANDIDATE, "configs/task-gate/mstr-000b.json"))
base_tasks = base_catalog["tasks"]
candidate_tasks = candidate_catalog["tasks"]

assert base_tasks["B019"]["canonical_state"] == "PENDING"
assert candidate_tasks["B019"]["canonical_state"] == "COMPLETE_CANONICAL"
expected_b019 = copy.deepcopy(base_tasks["B019"])
expected_b019["canonical_state"] = "COMPLETE_CANONICAL"
assert candidate_tasks["B019"] == expected_b019
for task_id, node in base_tasks.items():
    if task_id != "B019":
        assert candidate_tasks[task_id] == node

for task_id in ("B011", "B020", "B022"):
    assert candidate_tasks[task_id] == base_tasks[task_id]

assert candidate_tasks["B020"]["canonical_state"] == "PENDING"
assert candidate_tasks["B022"]["canonical_state"] == "PENDING"
assert candidate_tasks["B011"]["canonical_state"] == "BLOCKED"

tasks = read(CANDIDATE, "specs/002-code-model-supremacy-foundation/tasks.md")
assert "- [x] **B019 Freeze bounded teacher-rescue policy.**" in tasks
assert (
    "Canonical implementation: PR #78 / final head "
    "`25907c32fb60e83a6b171192e8c12c8092bc9f5e` / merge "
    "`ac68e2ff9de9962807ab32ce983b2e808bf4fab9`." in tasks
)
assert "- [ ] **B020 Freeze checkpoint-relative difficulty calibration contract.**" in tasks

evidence = read(CANDIDATE, "evidence/mstr-000b/B019-teacher-policy.md")
for phrase in (
    "**Implementation PR:** #78",
    "**Final implementation head:** `25907c32fb60e83a6b171192e8c12c8092bc9f5e`",
    "**Canonical implementation merge:** `ac68e2ff9de9962807ab32ce983b2e808bf4fab9`",
    "**State:** COMPLETE_CANONICAL",
    "run `33193446438` — SUCCESS",
    "run `33193784736` / job `98925641414` — SUCCESS",
    "run `33193968205` — SUCCESS",
    "run `33194149258` — SUCCESS",
    "MODEL_WEIGHT_ACCESS = NONE",
    "MODEL_EXECUTION = NONE",
    "TEACHER_API_EXECUTION = NONE",
    "PAID_MODEL_API = NONE",
    "NETWORK_TEACHER_CALL = NONE",
    "LARGE_DATASET_INGESTION = NONE",
    "WEIGHT_CHANGING_TRAINING = NONE",
    "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE",
    "B022_VERIFIER_HEALTH_AUTHORITY = NONE",
):
    assert phrase in evidence
