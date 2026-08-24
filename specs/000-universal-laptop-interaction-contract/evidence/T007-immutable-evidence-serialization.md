# T007 — Immutable Canonical Evidence Serialization

**Task:** MSTR-000 / T007  
**Canonical base:** `4ef6ff936061aeab1f04a4e346e25dcd3735475d`  
**Branch:** `task/000-t007-evidence-serialization`  
**Scope:** canonical JSON serialization, content identity, immutable persistence, and explicit supersession only. No model/runtime execution, model-weight access, network service, paid API, rented compute, or training.

## Semantics

T007 implements `MSTR canonical JSON v1` for evidence records:

- UTF-8 JSON;
- lexicographically sorted object keys;
- no insignificant whitespace;
- one trailing newline;
- native Unicode is preserved;
- non-finite floating-point values are rejected;
- non-JSON Python values and non-string object keys fail closed.

Finalized evidence is wrapped in `mstr.evidence-envelope.v1` and identified by SHA-256 of its exact canonical bytes. The canonical bytes—not a mutable in-memory mapping—are authoritative after finalization.

Persistence is content-addressed at `<sha256>.json` and uses create-exclusive write semantics. Repeating an identical write is idempotent. If an existing content-addressed path contains different bytes, the write fails rather than overwriting.

Corrections use explicit supersession metadata:

```text
supersedes = <previous evidence SHA-256>
supersession_reason = <required non-empty reason>
```

The old record remains immutable. Supersession-chain validation checks record integrity, requires a closed parent set, rejects duplicate identities, and rejects cycles.

## Exact prepared-source validation

An isolated sandbox was built from the canonical T005 `errors.py` / `ids.py` primitives plus the exact prepared T007 source/tests.

```text
Python = local tool environment
T007 focused tests = 18 passed
python -m compileall -q src = PASS
```

Focused coverage includes canonical byte stability, Unicode, NaN/Infinity rejection, non-JSON rejection, deterministic content identity, required correction reasons, write-once behavior, idempotent retries, hash mismatch, immutable-path conflicts, noncanonical input rejection, round trips, missing supersession parents, cycle detection, and forged finalized-record integrity.

The canonical T006 full-suite result remains `58 passed` as historical evidence. It was **not** re-run for T007 because the container cannot resolve GitHub to reconstruct the complete repository checkout; no T007 full-suite PASS is claimed. T007 is additive and does not modify prior T003–T006 source modules.

Ruff/mypy remain outside the local validation environment and are not claimed PASS; T011 remains the foundational quality-gate closeout.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```

## Result candidate

```text
T007_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T008
```
