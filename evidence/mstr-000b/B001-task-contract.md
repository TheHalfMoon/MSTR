# B001 — Machine Task Contracts Frozen

**Workstream:** MSTR-000B  
**Task:** B001  
**Canonical base at branch creation:** `e1b3cbd74ae0a74a80e3f345faef56da13818149`  
**Branch:** `feat/000b-b001-task-contracts`

## Bootstrap eligibility

B001 is one of the two explicit machine-gate bootstrap exceptions in the canonical MSTR-000B task graph. Manual prerequisite verification at branch creation established:

```text
MSTR_000B_SPEC_KIT = CANONICAL
B001_EXPLICIT_BOOTSTRAP_EXCEPTION = YES
B001_PREREQUISITES = NONE
EXTERNAL_EFFECT = NONE
NEW_MODEL_WEIGHT_ACCESS = NO
CANDIDATE_ARTIFACT_ACCESS = NO
PAID_COMPUTE = NO
LARGE_DATASET_INGESTION = NO
WEIGHT_CHANGING_TRAINING = NO
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

## Frozen contracts

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

Exact blob identities on the implementation branch:

```text
TASK_NODE_RUNTIME_BLOB = dcd823ce4251273da23f170a70cca9db35c9791d
TASK_NODE_DESIGN_BLOB  = dcd823ce4251273da23f170a70cca9db35c9791d
ELIGIBILITY_RUNTIME_BLOB = 759d0a2c0deff39be21eb19a0af576765debd5c0
ELIGIBILITY_DESIGN_BLOB  = 759d0a2c0deff39be21eb19a0af576765debd5c0
BYTE_IDENTICAL_DESIGN_RUNTIME = YES
```

## TaskNode v0

The contract freezes:

- task/workstream/title identity;
- canonical task state;
- exact prerequisite task IDs;
- output and evidence-output paths;
- candidate-dependent flag and candidate-pool requirement identity;
- external-effect class and exact authority identity;
- parallel-safety declaration;
- supersedes / superseded-by identities;
- machine-readable closeout terminal states and required output/evidence/merge conditions.

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

Every class above requires a non-empty `required_authority_id`. `candidate_dependent=true` independently requires a non-empty `candidate_pool_requirement_id`; candidate dependence does not itself grant external-effect authority.

The non-gated metadata classes are:

```text
NO_EXTERNAL_EFFECT
PUBLIC_METADATA_READ
TOKENIZER_METADATA_OR_SMALL_FILES
```

Their authority may be absent only when the canonical task itself permits that exact read and no gated effect is performed.

## TaskEligibilityResult v0

The structured result binds:

- exact task ID;
- exact 40-hex canonical main identity;
- prerequisite results including observed state and evidence presence;
- authority result;
- supersession result;
- canonical-state consistency result;
- candidate-pool result;
- deterministic reasons.

Fail-closed semantics are schema-enforced:

```text
eligible=true
  -> all represented checks satisfied=true
  -> top-level reasons=[]

eligible=false
  -> at least one top-level reason required
```

The validator implementation remains B002; B001 freezes only the machine contracts and does not create authority or mutate task state at runtime.

## Fixtures and focused validation

B001 adds:

- dedicated valid + invalid fixtures for both registered schemas;
- one explicit missing-authority fixture for every authority-gated external-effect class;
- one candidate-dependent fixture missing `candidate_pool_requirement_id`;
- a focused contract test proving those cases fail closed;
- generic schema-test support for per-schema fixture files and MSTR-000B-owned design sources.

Focused isolated validation command:

```text
PYTHONPATH=src pytest -q tests/contract/test_task_contracts.py tests/contract/test_schemas.py \
  -k 'task_contracts or mstr-task-node-v0 or mstr-task-eligibility-v0'
```

Result:

```text
22 passed, 34 deselected in 1.08s
```

This focused run reconstructed only the exact schema-loading surface needed for B001 because the execution environment could not clone GitHub over DNS. It is valid evidence for the new schema semantics, not a claim that the entire repository suite ran.

Additional gates in that isolated environment:

```text
RUFF = NOT_RUN / executable unavailable
MYPY_STRICT = NOT_RUN / executable unavailable
FULL_PYTEST = NOT_RUN / full repository checkout unavailable
CI = NOT_RUN / no exact-head workflow evidence claimed
```

No PASS is inferred for any unrun gate. Exact-head review and merge governance remain required before B001 becomes canonical.

## Authority state

```text
B001_AUTHORIZES_MODEL_ACCESS = NO
B001_AUTHORIZES_TRAINING = NO
B001_AUTHORIZES_PAID_COMPUTE = NO
B001_AUTHORIZES_LARGE_INGEST = NO
B002_TASK_ELIGIBILITY_VALIDATOR = STILL_PENDING
```
