from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mstr_qualify.task_gate import evaluate_task_snapshot

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "configs/task-gate/mstr-000b.json"
TASKS_FILE = "specs/001-agent-harness-verified-loop-foundation/tasks.md"
_CANONICAL_MAIN = "a" * 40


def _catalog() -> dict[str, Any]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_convergence_bindings_are_exact_and_fail_closed() -> None:
    catalog = _catalog()
    tasks = catalog["tasks"]
    unresolved = catalog["unresolved_bindings"]
    external = catalog["external_prerequisites"]

    assert set(unresolved) == {"B013"}
    assert tasks["B029"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert tasks["B029"]["prerequisites"] == [
        "A005",
        "A006",
        "A008",
        "A010",
        "B020",
    ]
    assert tasks["B030"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert tasks["B030"]["prerequisites"] == [
        "A007",
        "A008",
        "A009",
        "B024",
        "B025",
    ]
    assert tasks["B031"]["canonical_state"] == "PENDING"
    assert tasks["B031"]["prerequisites"] == [
        "A019",
        "A020",
        "B002",
        "B003",
        "B004",
        "B015",
        "B017",
        "B019",
        "B021",
        "B023",
        "B024",
        "B025",
        "B027",
        "B028",
        "B029",
        "B030",
    ]
    assert tasks["B011"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert tasks["B012"]["canonical_state"] == "PENDING"
    assert tasks["B012"]["external_effect_class"] == "MODEL_WEIGHT_ACCESS"
    assert tasks["B012"]["required_authority_id"] == (
        "B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION"
    )
    assert tasks["B011"]["required_authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
    assert tasks["B013"]["canonical_state"] == "BLOCKED"

    expected_paths = {
        "A005": "evidence/mstr-000a/A005-build-loop.md",
        "A006": "evidence/mstr-000a/A006-finalizer.md",
        "A007": "evidence/mstr-000a/A007-neutral-harness.md",
        "A008": "evidence/mstr-000a/A008-mstr-harness.md",
        "A009": "evidence/mstr-000a/A009-wepld-adapter.md",
        "A010": "evidence/mstr-000a/A010-capability-profile.md",
        "A019": "evidence/mstr-000a/A019-harness-tournament.md",
        "A020": "evidence/mstr-000a/A020-autoresearch.md",
    }
    for task_id, path in expected_paths.items():
        assert external[task_id] == {
            "workstream_id": "MSTR-000A",
            "tasks_file": TASKS_FILE,
            "state_evidence": path,
            "evidence_outputs": [path],
            "required_state": "COMPLETE_CANONICAL",
            "task_identity": f"MSTR-000A / {task_id}",
        }

    result = evaluate_task_snapshot("B031", canonical_main=_CANONICAL_MAIN)
    assert result["eligible"] is False
    prerequisite_rows = {row["task_id"]: row for row in result["prerequisite_results"]}
    assert prerequisite_rows["A019"]["satisfied"] is False
    assert prerequisite_rows["A020"]["satisfied"] is False
    assert "prerequisite.missing_task_binding" not in prerequisite_rows["A019"]["reasons"]
    assert "prerequisite.missing_task_binding" not in prerequisite_rows["A020"]["reasons"]


def test_incomplete_convergence_tasks_are_not_falsely_completed() -> None:
    tasks = _catalog()["tasks"]
    assert tasks["B029"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert tasks["B030"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert tasks["B031"]["canonical_state"] == "PENDING"
