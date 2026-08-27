# B001 — Machine Task Contract Implementation Evidence

**Workstream:** MSTR-000B  
**Task:** B001  
**State:** IMPLEMENTATION_ACTIVE / NOT_COMPLETE_CANONICAL  
**Canonical base at branch creation:** `e1b3cbd74ae0a74a80e3f345faef56da13818149`  
**Branch:** `feat/000b-b001-task-contracts`  
**Last implementation head before this evidence refresh:** `ccda5c748157fa91417d0be112296e03eb6cb8ee`

This document is implementation evidence only. B001 remains unchecked until the required exact-head quality gates, exact-head review, merge, and canonical closeout are all satisfied.

## Bootstrap eligibility

B001 is one of the two explicit machine-gate bootstrap exceptions in the canonical MSTR-000B task graph. Live prerequisite reconciliation before the latest implementation mutations established:

```text
CANONICAL_MAIN = e1b3cbd74ae0a74a80e3f345faef56da13818149
MSTR_000B_SPEC_KIT = CANONICAL / PR_39_MERGED
B001_EXPLICIT_BOOTSTRAP_EXCEPTION = YES
B001_PREREQUISITES = NONE
PR_38_A003 = MERGED_CANONICAL
A001_A002 = COMPLETE_CANONICAL
EXTERNAL_EFFECT = NONE
NEW_MODEL_WEIGHT_ACCESS = NO
CANDIDATE_ARTIFACT_ACCESS = NO
PAID_COMPUTE = NO
LARGE_DATASET_INGESTION = NO
WEIGHT_CHANGING_TRAINING = NO
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

The corresponding `implementation-readiness.md` B001 entry checks are now reconciled to those live facts. This establishes implementation eligibility; it does not establish B001 completion.

## Contract identities

Runtime schemas:

```text
schemas/mstr-task-node-v0.schema.json
schemas/mstr-task-eligibility-v0.schema.json
```

Design sources:

```text
specs/002-code-model-supremacy-foundation/contracts/mstr-task-node-v0.schema.json
specs/002-code-model-supremacy-foundation/contracts/mstr-task-eligibility-v0.schema.json
```

Exact current blob identities at the last implementation head above:

```text
TASK_NODE_RUNTIME_BLOB = c93b28cb31d0ec34fad69683adcb211a4b6d18f6
TASK_NODE_DESIGN_BLOB  = c93b28cb31d0ec34fad69683adcb211a4b6d18f6
ELIGIBILITY_RUNTIME_BLOB = bc01717c71678df6334f9c2eac9ae9003924bd29
ELIGIBILITY_DESIGN_BLOB  = bc01717c71678df6334f9c2eac9ae9003924bd29
BYTE_IDENTICAL_DESIGN_RUNTIME = YES
```

Any later schema mutation invalidates these identities and requires a fresh evidence refresh.

## TaskNode v0

The contract freezes:

- task/workstream/title identity;
- canonical task state;
- exact prerequisite task IDs;
- repository-relative output and evidence-output paths;
- candidate-dependent flag and candidate-pool requirement identity;
- external-effect class and exact authority identity;
- parallel-safety declaration;
- supersedes / superseded-by identities;
- machine-readable closeout terminal states and required output/evidence/merge conditions.

Repository paths fail closed on POSIX absolute paths, parent traversal, Windows drive/colon qualification, and backslash-separated paths.

Closeout is fail-closed: `terminal_states[]` may contain only `COMPLETE_CANONICAL`, `SUPERSEDED_CANONICAL`, or an explicit `NOT_REQUIRED...` state. `PENDING`, `ACTIVE`, and `BLOCKED` cannot be declared terminal closeout states.

Authority-gated external-effect classes are exactly:

```text
MODEL_WEIGHT_ACCESS
GATED_TERMS_ACCEPTANCE
PAID_MODEL_API_EXECUTION
PAID_COMPUTE
RENTED_COMPUTE
LARGE_DATASET_INGESTION
WEIGHT_CHANGING_TRAINING
LONG_TRAINING
LARGE_SCALE_RL
PRODUCTION_RELEASE
```

Every class above requires a non-empty `required_authority_id`. That identifier is a foreign-key reference to an already-canonical authority record/envelope. The referenced authority owns exact effect scope and any applicable cost/resource ceilings. TaskNode validation never creates or widens authority, and scope/cost limits are intentionally not duplicated into a second mutable authority surface.

`candidate_dependent=true` independently requires a non-empty `candidate_pool_requirement_id`; candidate dependence does not itself grant external-effect authority.

The non-gated metadata classes are:

```text
NO_EXTERNAL_EFFECT
PUBLIC_METADATA_READ
TOKENIZER_METADATA_OR_SMALL_FILES
```

## TaskEligibilityResult v0

The structured result binds:

- exact task ID;
- exact TaskNode schema version and SHA-256 identity;
- exact 40-hex canonical main identity;
- prerequisite results including observed state and evidence presence;
- authority result;
- supersession result;
- canonical-state consistency result;
- candidate-pool result;
- explicit semantic-check completion flags;
- deterministic reasons.

Fail-closed semantics are schema-enforced:

```text
eligible=true
  -> every represented check satisfied=true
  -> every prerequisite has observed state + evidence
  -> superseded=false
  -> superseded_by=[]
  -> state consistency has an observed state
  -> semantic cross-contract checks are true
  -> nested failure reasons are empty
  -> top-level reasons=[]
  -> if candidate_pool_result.required=true, observed_pool_id is non-empty

superseded=true
  -> superseded_by has at least one task identity

superseded=false
  -> superseded_by=[]

eligible=false
  -> at least one top-level reason required
  -> missing prerequisite/state/pool observations remain representable as null/false evidence
```

A required but unavailable candidate pool is therefore representable as `eligible=false`, `required=true`, `requirement_id=<expected>`, `observed_pool_id=null`, `satisfied=false`; the schema does not erase the failure state it is designed to report.

The B002 validator remains responsible for computing and verifying these semantics against canonical repository truth. B001 freezes contracts only; it grants no authority and performs no task-state mutation.

## Fixtures and regression coverage

B001 now includes coverage for:

- dedicated valid + invalid fixtures for both registered schemas;
- every authority-gated external-effect class missing authority;
- candidate-dependent task missing `candidate_pool_requirement_id`;
- nonterminal closeout states;
- POSIX absolute, parent-traversal, Windows drive/colon, and backslash paths;
- eligible prerequisite results without evidence;
- eligible superseded results;
- contradictory `superseded=false` + non-empty `superseded_by` results;
- eligible required-candidate-pool results without observed pool identity;
- unavailable required pool remaining representable when `eligible=false`;
- `eligible=false` without a reason;
- explicit-file CLI auto-detection for both B001 schema versions;
- CLI schema self-check requiring a valid and invalid fixture for every registered schema;
- generic schema-test support for per-schema fixture files and MSTR-000B-owned design sources.

## Historical validation — stale after head changes

A prior isolated focused run reported:

```text
27 passed, 34 deselected in 1.27s
```

That run predates subsequent schema/CLI/test/review hardening. It is retained only as historical evidence and MUST NOT be reported as an exact-current-head PASS.

```text
HISTORICAL_FOCUSED_RESULT = STALE_AFTER_HEAD_CHANGE
```

## Required exact-head quality gates

`configs/quality.toml` requires all of:

```text
pytest -q
ruff check src tests
mypy
python -m mstr_qualify validate
```

Current qualification environment status after the latest implementation changes:

```text
FULL_PYTEST = NOT_RUN / exact repository checkout unavailable in current execution environment
RUFF = UNAVAILABLE / executable absent; local no-index installation also unavailable
MYPY_STRICT = UNAVAILABLE / executable absent; local no-index installation also unavailable
OFFLINE_SCHEMA_SELFCHECK = NOT_RUN / exact full repository checkout unavailable
CI = NOT_RUN / repository quality config explicitly records no generic CI workflow and no exact-head quality workflow is claimed
```

These are not PASS states. Because the quality gates are mandatory before `COMPLETE_CANONICAL`, B001 remains open and must not merge until a tool environment capable of executing the exact head records the required passing results.

## Review state

Earlier Qodo findings about premature completion, authority-envelope representation, CLI schema dispatch, dedicated-fixture self-checking, prerequisite evidence, supersession, and Windows path handling were remediated or rendered outdated by later commits. CodeRabbit's contradictory-supersession finding was also fixed with a bidirectional invariant and regression test.

A fresh exact-current-head review is still required after the final evidence/PR-body update. No earlier review is reused as final-head evidence.

## Authority state

```text
B001_AUTHORIZES_MODEL_ACCESS = NO
B001_AUTHORIZES_TRAINING = NO
B001_AUTHORIZES_PAID_COMPUTE = NO
B001_AUTHORIZES_LARGE_INGEST = NO
B001_AUTHORIZES_PRODUCTION_RELEASE = NO
B002_TASK_ELIGIBILITY_VALIDATOR = STILL_PENDING
B001_COMPLETE_CANONICAL = NO
```
