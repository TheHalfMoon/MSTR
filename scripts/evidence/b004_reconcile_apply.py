from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} match count: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


current = Path("docs/canonical/CURRENT_STATE.md")
replace_once(
    current,
    """CANONICAL_MAIN_AT_LATEST_RECONCILIATION = 2c02eb68a32264c86f69eb7ffc1c99ad87328376
CANONICAL_TREE = 4d0688aaabb903d7bcfdf15728bcd138ce179fcc
PROJECT_PHASE = PRETRAINING_FOUNDATION / MSTR-000A_EARLY_IMPLEMENTATION + MSTR-000B_PLANNING
ACTIVE_IMPLEMENTATION_SPEC = MSTR-000A
ACTIVE_IMPLEMENTATION_TASK = A004_AGENT_STATE / NEXT_ELIGIBLE_AFTER_A003
PLANNING_SPEC = MSTR-000B_CODE_MODEL_SUPREMACY_FOUNDATION
OPEN_PLANNING_PR_AT_RECONCILIATION = #39
PR_39_BRANCH = docs/002-code-model-supremacy-foundation
""",
    """CANONICAL_MAIN_AT_LATEST_RECONCILIATION = d0e90740924f6991da361536e7f835eb55ae9145
CANONICAL_TREE = c602b5142a31abe55d3519913f5badfaa27469cc
PROJECT_PHASE = PRETRAINING_FOUNDATION / MSTR-000A_EARLY_SAFE + MSTR-000B_GOVERNANCE_EXECUTION
ACTIVE_IMPLEMENTATION_SPEC = MSTR-000B
ACTIVE_IMPLEMENTATION_TASK = B004_000A_SEQUENCE_RECONCILIATION / ENTRY_GATE_PROVEN
PLANNING_SPEC = NONE_SEPARATE / MSTR-000B_CANONICAL
MSTR_000B_PLANNING_PR = #39 / MERGED e1b3cbd74ae0a74a80e3f345faef56da13818149
LAST_COMPLETE_MSTR_000B_TASK = B003 / CLOSEOUT_MERGE d0e90740924f6991da361536e7f835eb55ae9145
NEXT_ELIGIBLE_MSTR_000B_TASK = B004
""",
    "current-state repository header",
)
replace_once(
    current,
    "## Canonical History Through A003",
    "## Canonical History Through A004",
    "current-state history heading",
)
replace_once(
    current,
    """A001 = COMPLETE_CANONICAL / LOOP_CONTRACT_V0
A002 = COMPLETE_CANONICAL / RUN_EVENT_V0
A003 = COMPLETE_CANONICAL / EVENT_LOG_AND_DETERMINISTIC_REPLAY
""",
    """A001 = COMPLETE_CANONICAL / LOOP_CONTRACT_V0
A002 = COMPLETE_CANONICAL / RUN_EVENT_V0
A003 = COMPLETE_CANONICAL / EVENT_LOG_AND_DETERMINISTIC_REPLAY
A004 = COMPLETE_CANONICAL / AGENT_STATE_PROJECTION_AND_BOUNDED_COMPACTION
A005-A018 = PENDING / EARLY_SAFE_ONLY_WHEN_EXACT_PREREQUISITES_PASS
A019-A024 = PENDING / CONVERGENCE_GATED
""",
    "current-state A-task ledger",
)
replace_once(
    current,
    """Historical head gates do not transfer to later heads. No CI PASS is claimed for PR #38.

## MSTR-000A Next State

A003 is no longer active. Under the early-safe sequence amendment proposed by MSTR-000B, the next model-independent task is:

```text
A004 = AgentState projection + bounded compaction
```

A004 must still satisfy its exact canonical prerequisites at execution time. Candidate-dependent A019-A024 remain convergence-gated and may not consume an incomplete or incomparable candidate pool.
""",
    """Historical head gates do not transfer to later heads. No CI PASS is claimed for PR #38.

A004 canonical implementation and closeout:

```text
IMPLEMENTATION_PR = #45
FINAL_IMPLEMENTATION_HEAD = d0098548766232c9fa1a879941978d1735ef9e4a
IMPLEMENTATION_MERGE = 564096fc9e8ec3e2b0aa9505926e15f66b00ce74
CLOSEOUT_PR = #46
CLOSEOUT_HEAD = c91d603ab3175260348706b3f879b86900511510
CLOSEOUT_MERGE = c2d0ee8a6b9d47275c4d309cd187c1ed0d35fb02
STATE = COMPLETE_CANONICAL
```

## MSTR-000A Next State

A001-A004 are canonical. The next MSTR-000A early-safe task is A005, but B004 does not execute or authorize A005. A005-A018 remain individually gated by their exact prerequisites and the machine task validator where represented. Candidate-dependent A019-A024 remain convergence-gated and may not consume an incomplete or incomparable candidate pool.
""",
    "current-state A004 reconciliation",
)
replace_once(
    current,
    """Until PR #39 is reviewed and merged, the MSTR-000B planning amendment is evidence only; live `main` remains canonical.

## MSTR-000B Planning

Planning branch at this checkpoint:

```text
BRANCH = docs/002-code-model-supremacy-foundation
PR = #39
WORKSTREAM = MSTR-000B
TITLE = Code Model Supremacy Pre-Training Foundation
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED
NEW_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_PLANNING_ALONE
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
```
""",
    """PR #39 merged as `e1b3cbd74ae0a74a80e3f345faef56da13818149`; the MSTR-000B sequence amendment is canonical. B004 records the later live reconciliation after A004 and the B001-B003 governance chain. It does not rewrite or reopen A001-A004.

## MSTR-000B Canonical Foundation

```text
PLANNING_PR = #39 / MERGED
PLANNING_MERGE = e1b3cbd74ae0a74a80e3f345faef56da13818149
WORKSTREAM = MSTR-000B
TITLE = Code Model Supremacy Pre-Training Foundation
B001 = COMPLETE_CANONICAL
B002 = COMPLETE_CANONICAL
B003 = COMPLETE_CANONICAL
B004 = ENTRY_GATE_PROVEN / IMPLEMENTATION_ACTIVE
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED
NEW_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_PLANNING_ALONE
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
```
""",
    "current-state B planning status",
)

roadmap = Path("docs/canonical/PROGRAM_ROADMAP.md")
replace_once(
    roadmap,
    """Convergence requires equivalent candidate qualification and the MSTR-000B stable candidate/verifier/research prerequisites.

**Builds and qualifies:**
""",
    """Convergence requires equivalent candidate qualification and the MSTR-000B stable candidate/verifier/research prerequisites.

Canonical early-safe history reconciled by MSTR-000B B004:

```text
A001 + A002 = COMPLETE_CANONICAL / PR #37 / merge 5693749dd560979496efad488789ec35b2c2a84d
A003 = COMPLETE_CANONICAL / PR #38 / head 41122ae8dee65b2a6b3c6b188cf335d74088b06f / merge 2c02eb68a32264c86f69eb7ffc1c99ad87328376
A004 = COMPLETE_CANONICAL / PR #45 / merge 564096fc9e8ec3e2b0aa9505926e15f66b00ce74 / closeout PR #46 / merge c2d0ee8a6b9d47275c4d309cd187c1ed0d35fb02
A005-A018 = PENDING / EARLY_SAFE only when each exact prerequisite passes
A019-A024 = PENDING / CONVERGENCE_GATED
```

This ledger records live history; it does not reopen completed A-tasks or pre-authorize pending ones.

**Builds and qualifies:**
""",
    "roadmap A reconciliation ledger",
)

tasks = Path("specs/001-agent-harness-verified-loop-foundation/tasks.md")
replace_once(
    tasks,
    """T029–T034 in MSTR-000 remain active according to their own canonical state and are not reopened by this package. No A-task may bypass an explicit external-effect gate. The machine task validator introduced by MSTR-000B becomes authoritative for eligibility once canonical.

## Phase A — Contract and Replay Spine
""",
    """T029–T034 in MSTR-000 remain active according to their own canonical state and are not reopened by this package. No A-task may bypass an explicit external-effect gate. The machine task validator introduced by MSTR-000B becomes authoritative for eligibility once canonical.

### Live history reconciliation

MSTR-000B B004 binds the sequence amendment to the repository's actual canonical history without rewriting it:

```text
A001 + A002 = COMPLETE_CANONICAL / PR #37 / head b4547f9393644586f893f5cd7ddd420f82bc6f2a / merge 5693749dd560979496efad488789ec35b2c2a84d
A003 = COMPLETE_CANONICAL / PR #38 / head 41122ae8dee65b2a6b3c6b188cf335d74088b06f / merge 2c02eb68a32264c86f69eb7ffc1c99ad87328376
A004 = COMPLETE_CANONICAL / PR #45 / head d0098548766232c9fa1a879941978d1735ef9e4a / merge 564096fc9e8ec3e2b0aa9505926e15f66b00ce74 / closeout PR #46 / merge c2d0ee8a6b9d47275c4d309cd187c1ed0d35fb02
A005-A018 = PENDING / EARLY_SAFE only with exact prerequisites
A019-A024 = PENDING / CONVERGENCE_GATED
```

This reconciliation does not infer completion for A005+ and grants no external-effect authority.

## Phase A — Contract and Replay Spine
""",
    "000A task live-history reconciliation",
)

evidence = Path("evidence/mstr-000b/B004-000a-sequence-reconciliation.md")
if evidence.exists():
    raise SystemExit("B004 evidence already exists")
evidence.parent.mkdir(parents=True, exist_ok=True)
evidence.write_text(
    """# B004 — MSTR-000A Sequence Reconciliation Evidence

**Workstream:** MSTR-000B
**Task:** B004
**State:** IMPLEMENTATION_ACTIVE
**Entry canonical main:** `d0e90740924f6991da361536e7f835eb55ae9145`

## Exact-main entry gate

B003 closeout PR #51 merged exact qualified/reviewed head `711b81d17fdcd941c881fb3e27ad6494fb271a0b` as canonical merge `d0e90740924f6991da361536e7f835eb55ae9145`.

Post-closeout verification run `33095418967`, job `98598942120`, proved on that exact canonical main:

```text
B003 = terminal / COMPLETE_CANONICAL
B004 = eligible=true
canonical drift = clean
targeted governance tests = PASS (54 passed)
pytest -q = PASS (498 passed)
ruff check src tests = PASS
mypy = PASS (26 source files)
python -m mstr_qualify validate = PASS
```

No B004 material mutation began before that production `eligible=true` result.

## Reconciled canonical history

| Task | Canonical truth |
| --- | --- |
| A001 | `COMPLETE_CANONICAL`; PR #37; head `b4547f9393644586f893f5cd7ddd420f82bc6f2a`; merge `5693749dd560979496efad488789ec35b2c2a84d` |
| A002 | `COMPLETE_CANONICAL`; PR #37; head `b4547f9393644586f893f5cd7ddd420f82bc6f2a`; merge `5693749dd560979496efad488789ec35b2c2a84d` |
| A003 | `COMPLETE_CANONICAL`; PR #38; head `41122ae8dee65b2a6b3c6b188cf335d74088b06f`; merge `2c02eb68a32264c86f69eb7ffc1c99ad87328376` |
| A004 | `COMPLETE_CANONICAL`; implementation PR #45; head `d0098548766232c9fa1a879941978d1735ef9e4a`; merge `564096fc9e8ec3e2b0aa9505926e15f66b00ce74`; closeout PR #46; merge `c2d0ee8a6b9d47275c4d309cd187c1ed0d35fb02` |
| A005-A018 | `PENDING`; `EARLY_SAFE` only when each task's exact prerequisites pass |
| A019-A024 | `PENDING`; `CONVERGENCE_GATED` |

PR #39, which introduced MSTR-000B and the corrected sequence amendment, is canonical at merge `e1b3cbd74ae0a74a80e3f345faef56da13818149`.

## Entry-semantics reconciliation

The historical blanket rule:

```text
ENTRY_GATE = T034_COMPLETE_CANONICAL
```

is not the live authorization rule for all MSTR-000A work. The canonical split is:

```text
EARLY_SAFE = A001-A018
  only when each exact prerequisite is satisfied
  and no unqualified candidate result or external authority is consumed

CONVERGENCE = A019-A024
  only after stable/equivalent candidate qualification
  + the exact MSTR-000B prerequisites declared by the task graph
```

This records the actual history rather than retroactively pretending A001-A004 waited for T034. It does not reopen completed tasks, mark A005+ complete, or weaken any external-effect gate.

## Amended canonical surfaces

This B004 implementation is intentionally documentation/governance-only:

- `docs/canonical/CURRENT_STATE.md` — advances the stale A003-era snapshot to the verified B003/A004-era truth;
- `docs/canonical/PROGRAM_ROADMAP.md` — records the canonical A001-A004 ledger under the already-adopted EARLY_SAFE/CONVERGENCE semantics;
- `specs/001-agent-harness-verified-loop-foundation/tasks.md` — binds the sequence amendment to exact PR/head/merge history;
- this evidence record.

No source code, runtime behavior, task-gate implementation, candidate record, model artifact, or training configuration changes in B004 implementation.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API_EXECUTION = NONE
PAID_COMPUTE = NONE
RENTED_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
PRIVATE_USER_TRACE_INGESTION = NONE
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

## Closeout rule

B004 remains `IMPLEMENTATION_ACTIVE` until this exact implementation head is independently qualified and reviewed, merged with an expected-head guard, and post-merge canonical main is verified. A separate closeout must then align the MSTR-000B B004 task checkbox/catalog/evidence state. B005 or any other successor work must use its own exact eligibility gate and authority boundary; B004 grants none by implication.
""",
    encoding="utf-8",
)
