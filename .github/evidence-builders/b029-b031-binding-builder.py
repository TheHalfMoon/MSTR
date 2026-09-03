from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".")
CATALOG_PATH = ROOT / "configs/task-gate/mstr-000b.json"
TASKS_FILE = "specs/001-agent-harness-verified-loop-foundation/tasks.md"

EVIDENCE_PATHS = {
    "A004": "evidence/mstr-000a/A004-agent-state.md",
    "A005": "evidence/mstr-000a/A005-build-loop.md",
    "A006": "evidence/mstr-000a/A006-finalizer.md",
    "A007": "evidence/mstr-000a/A007-neutral-harness.md",
    "A008": "evidence/mstr-000a/A008-mstr-harness.md",
    "A009": "evidence/mstr-000a/A009-wepld-adapter.md",
    "A010": "evidence/mstr-000a/A010-capability-profile.md",
    "A015": "evidence/mstr-000a/A015-direction-to-done.md",
    "A016": "evidence/mstr-000a/A016-metrics.md",
    "A019": "evidence/mstr-000a/A019-harness-tournament.md",
    "A020": "evidence/mstr-000a/A020-autoresearch.md",
}

EVIDENCE_TEXT = """# B029–B031 Cross-Workstream Binding Reconciliation

**Workstream:** MSTR-000B  
**State:** RECONCILED_PENDING_CANONICAL_MERGE  
**Canonical base:** `b20349c23ada1130f98e28c0e1e3db56ed692d13`

## Purpose

Replace three prose-only fail-closed bindings with exact repository-owned MSTR-000A prerequisite identities. This is task-gate governance repair only. It does not execute B029, B030, A019, A020, B031, or any external effect.

## B029 binding

B029 freezes adaptive test-time compute and selective-context policy. The exact already-canonical MSTR-000A surfaces required before B029 may execute are:

- `A004` — authoritative `AgentState`, uncertainty retention, and bounded compaction;
- `A005` — `MSTR-BUILD-LOOP-v0`, repair/timeout/tool budgets, and recovery semantics;
- `A006` — protected verifier/finalizer authority;
- `A008` — explicit selective context plus bounded recovery cadence;
- `A010` — evidence-derived reliable context budget, verifier cadence, and repair-depth contract.

B020 remains the MSTR-000B checkpoint-relative difficulty prerequisite. The candidate changes B029 from `BLOCKED` to `PENDING`; the machine gate must prove every bound prerequisite `COMPLETE_CANONICAL` before returning `eligible=true`.

## B030 binding

B030 freezes Repository Health Delta and cross-harness robustness evaluation. Its already-canonical A019-ready surfaces are:

- `A007` — H0 neutral-minimal harness;
- `A008` — H1 MSTR-native harness;
- `A009` — H2 WePLD-native adapter;
- `A015` — Direction-to-Done task taxonomy used for comparable task cells;
- `A016` — DVCR/TTVC diagnostic metric surface that B030 explicitly extends with Repository Health Delta.

B024/B025 remain the MSTR-000B test-generation and feature/greenfield curriculum prerequisites. The candidate changes B030 from `BLOCKED` to `PENDING`; eligibility remains machine-derived.

## B031 binding

B031 already names A019 and A020 as prerequisites. This reconciliation binds them to the MSTR-000A canonical checklist and their exact required evidence paths:

- `A019` -> `evidence/mstr-000a/A019-harness-tournament.md`;
- `A020` -> `evidence/mstr-000a/A020-autoresearch.md`.

Both tasks remain incomplete. Therefore B031 remains ineligible after this repair, but for real unsatisfied prerequisites rather than `prerequisite.missing_task_binding`. No A019/A020 completion is inferred.

## Preserved hard stops

```text
B011_AUTHORITY_CHANGE = NONE
B013_CANDIDATE_POOL_BINDING_CHANGE = NONE
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
```

B011 remains separately blocked on the exact founder authority required by canonical B010. B013 remains separately blocked on candidate qualification/convergence. This repair creates no authority and cannot satisfy either gate.
"""

TEST_TEXT = '''from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "configs/task-gate/mstr-000b.json"
TASKS_FILE = "specs/001-agent-harness-verified-loop-foundation/tasks.md"


def _catalog() -> dict[str, Any]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_convergence_bindings_are_exact_and_fail_closed() -> None:
    catalog = _catalog()
    tasks = catalog["tasks"]
    unresolved = catalog["unresolved_bindings"]
    external = catalog["external_prerequisites"]

    assert set(unresolved) == {"B011", "B013"}
    assert tasks["B029"]["canonical_state"] == "PENDING"
    assert tasks["B029"]["prerequisites"] == [
        "A004",
        "A005",
        "A006",
        "A008",
        "A010",
        "B020",
    ]
    assert tasks["B030"]["canonical_state"] == "PENDING"
    assert tasks["B030"]["prerequisites"] == [
        "A007",
        "A008",
        "A009",
        "A015",
        "A016",
        "B024",
        "B025",
    ]
    assert tasks["B031"]["canonical_state"] == "PENDING"
    assert tasks["B011"]["canonical_state"] == "BLOCKED"
    assert tasks["B013"]["canonical_state"] == "BLOCKED"

    expected_paths = {
        "A004": "evidence/mstr-000a/A004-agent-state.md",
        "A005": "evidence/mstr-000a/A005-build-loop.md",
        "A006": "evidence/mstr-000a/A006-finalizer.md",
        "A007": "evidence/mstr-000a/A007-neutral-harness.md",
        "A008": "evidence/mstr-000a/A008-mstr-harness.md",
        "A009": "evidence/mstr-000a/A009-wepld-adapter.md",
        "A010": "evidence/mstr-000a/A010-capability-profile.md",
        "A015": "evidence/mstr-000a/A015-direction-to-done.md",
        "A016": "evidence/mstr-000a/A016-metrics.md",
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


def test_incomplete_convergence_tasks_are_not_falsely_completed() -> None:
    tasks = _catalog()["tasks"]
    assert tasks["B029"]["canonical_state"] == "PENDING"
    assert tasks["B030"]["canonical_state"] == "PENDING"
    assert tasks["B031"]["canonical_state"] == "PENDING"
'''


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    external = catalog["external_prerequisites"]
    for task_id, path in EVIDENCE_PATHS.items():
        external[task_id] = {
            "workstream_id": "MSTR-000A",
            "tasks_file": TASKS_FILE,
            "state_evidence": path,
            "evidence_outputs": [path],
            "required_state": "COMPLETE_CANONICAL",
            "task_identity": f"MSTR-000A / {task_id}",
        }

    tasks = catalog["tasks"]
    tasks["B029"]["canonical_state"] = "PENDING"
    tasks["B029"]["prerequisites"] = [
        "A004",
        "A005",
        "A006",
        "A008",
        "A010",
        "B020",
    ]
    tasks["B030"]["canonical_state"] = "PENDING"
    tasks["B030"]["prerequisites"] = [
        "A007",
        "A008",
        "A009",
        "A015",
        "A016",
        "B024",
        "B025",
    ]
    tasks["B031"]["canonical_state"] = "PENDING"

    unresolved = catalog["unresolved_bindings"]
    for task_id in ("B029", "B030", "B031"):
        unresolved.pop(task_id, None)

    CATALOG_PATH.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    evidence_path = (
        ROOT
        / "evidence/mstr-000b/"
        / "B029-B031-cross-workstream-binding-reconciliation.md"
    )
    evidence_path.write_text(EVIDENCE_TEXT, encoding="utf-8")
    test_path = ROOT / "tests/contract/test_convergence_external_bindings.py"
    test_path.write_text(TEST_TEXT, encoding="utf-8")


if __name__ == "__main__":
    main()
