# A005 — MSTR-BUILD-LOOP-v0 Implementation Evidence

**Task:** `A005`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `8c3faa1d66409cd44cd39040380ed326175b6b34`

## Entry Gate

A005 is model-independent early-safe MSTR-000A work. The canonical entry state proves:

```text
A001 = COMPLETE_CANONICAL
A002 = COMPLETE_CANONICAL
A003 = COMPLETE_CANONICAL
A004 = COMPLETE_CANONICAL
UNQUALIFIED_CANDIDATE_RESULT_REQUIRED = NO
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
```

The repository has no machine-readable MSTR-000A task catalog; A005 therefore uses the canonical Spec 001 manual exact-prerequisite rule. The implementation order in `quickstart.md` and `plan.md` places the Build Loop after A001-A004 contracts/event/state foundations and before A006 protected finalizer semantics.

## Implementation Scope

A005 introduces `src/mstr_qualify/harness/build_loop.py` as the smallest framework-neutral bounded state graph required by `MSTR-BUILD-LOOP-v0`.

The implementation provides:

- conceptual states `ORIENT`, `GOAL`, `LOCALIZE`, `PLAN`, `ACT`, `OBSERVE`, `VERIFY`, `RECOVER`, `STOP`;
- legal non-linear transitions rather than a forced ritual sequence;
- the required trivial fast path `ORIENT -> GOAL -> ACT -> VERIFY -> STOP`;
- exact `mstr.loop-contract.v0` validation before loop construction;
- fail-closed step, tool-call, repair, and timeout budgets;
- recovery rejection for retrying the same failed action without new evidence;
- stop proposal semantics that require a verifier observation for ordinary STOP;
- explicit escalation semantics when permitted by the frozen loop contract;
- no API that lets the builder convert its own stop proposal into canonical success.

A006 remains responsible for deriving `VERIFIED_SUCCESS` / `RECOVERED_SUCCESS` from protected verifier results.

## Security / Authority Boundary

Repository/model text cannot grant success authority. A normal builder STOP proposed outside VERIFY, without a verifier observation, through a direct state transition, after budget exhaustion, or after timeout fails closed.

This task performs no external effect and grants no new authority.

## Required Qualification

The candidate is not canonical completion evidence until exact-head qualification proves:

```text
pytest -q tests/unit/test_build_loop.py
mstr-qualify validate
pytest -q
ruff check src tests
mypy src
```

A005 remains unchecked in `tasks.md` until the implementation is reviewed, guarded-merged, post-merge verified, and separately canonicalized through the repository closeout lifecycle.
