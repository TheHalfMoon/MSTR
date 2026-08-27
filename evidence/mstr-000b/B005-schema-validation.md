# B005 — Task-Local Schema Validation

**Task:** MSTR-000B / B005  
**Purpose:** validate the two B005 machine-readable evidence outputs without expanding the shared `mstr_qualify` runtime contract registry.  
**Exact reviewed head before this evidence-only commit:** `efe1561fa60ab228b9bfd602f9f3a2f16e262b3d`

## Contract ownership

B005 is a metadata-rescan task. Its JSON outputs are task-local evidence formats, not shared runtime records consumed by the qualification CLI. Registering them in `src/mstr_qualify/schemas.py` / CLI auto-detection would expand B005 into runtime implementation and collide with the active B001 shared-governance contract work without a canonical requirement to do so.

The repository's merge discipline still requires schema-valid outputs. B005 therefore owns explicit Draft 2020-12 task-local schemas:

```text
DISCOVERY_SCHEMA = specs/002-code-model-supremacy-foundation/contracts/b005-code-backbone-discovery-v1.schema.json
DISCOVERY_SCHEMA_BLOB = 8d3ae16e6a8ec134b36cd6d10c73ca5418f058dd

INPUT_BINDING_SCHEMA = specs/002-code-model-supremacy-foundation/contracts/b005-canonical-input-binding-v1.schema.json
INPUT_BINDING_SCHEMA_BLOB = 419e0a363850f833ad1f6150c4a58fa59785e314

DISCOVERY_INSTANCE = artifacts/manifests/B005-code-backbone-discovery.json
DISCOVERY_INSTANCE_BLOB = daf641bcd10af01a677a69a3a35e0d411ab6488b

INPUT_BINDING_INSTANCE = artifacts/manifests/B005-canonical-input-binding.json
INPUT_BINDING_INSTANCE_BLOB = a6a4d8ac1c9a951ee999e045986fd50ca8a21ef4
```

## Targeted validation

Execution environment:

```text
Python = 3.13.5
jsonschema = 4.26.0
validator = Draft202012Validator
network = not required
model access = none
```

The decoded schema content was self-checked with `Draft202012Validator.check_schema`. Each current B005 instance was then validated against its task-local schema.

```text
DISCOVERY_SCHEMA_DRAFT_2020_12_SELF_CHECK = PASS
INPUT_BINDING_SCHEMA_DRAFT_2020_12_SELF_CHECK = PASS
DISCOVERY_CURRENT_INSTANCE = PASS
INPUT_BINDING_CURRENT_INSTANCE = PASS
```

Fail-closed negative mutations were also checked:

```text
DISCOVERY_MUTATION: scope.model_weight_access = true
RESULT = REJECTED

INPUT_BINDING_MUTATION: authority.creates_model_access_authority = true
RESULT = REJECTED
```

The schemas additionally freeze the B005 identity, canonical-main SHA shape, revision-status/revision-shape relationship, input Git blob SHA shape, and no-authority/no-weight-access invariants.

## Shared CLI boundary

`python -m mstr_qualify validate <file>` intentionally auto-detects only **registered shared runtime contracts** through `schema_version`. B005 task-local evidence uses `format_version` and is not silently added to that shared registry. This is deliberate scope separation, not a claim that the generic CLI validates arbitrary JSON files.

If a later canonical task promotes either B005 format into a reusable runtime contract, that task must register it, add canonical valid/invalid fixtures, and run the ordinary runtime contract gates at that time.

## External-effect statement

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

This evidence creates no candidate admission or model-access authority.

## Canonical refresh validation — 2026-08-27

The historical instance identities above remain evidence for PR #41. The canonical B005 refresh supersedes those *instance* blobs for current closeout purposes while retaining the same two task-local Draft 2020-12 schemas.

```text
REFRESH_CANONICAL_MAIN = 986b174b2bf79ce53a3e67b9b02c55cbe6981303
REFRESH_ENTRY_GATE_RUN = 33103275261
REFRESH_ENTRY_GATE_JOB = 98626338825
PUBLIC_METADATA_NETWORK = huggingface.co/api/models/<repo> ONLY
MODEL_WEIGHT_ACCESS = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
GATED_TERMS_ACCEPTANCE = NONE
```

The guarded refresh workflow MUST, before pushing its candidate head:

1. self-check both Draft 2020-12 schemas;
2. validate both refreshed JSON instances;
3. reject negative mutations that set `scope.model_weight_access=true` or `authority.creates_model_access_authority=true`;
4. verify every canonical-input Git blob against exact canonical main;
5. run the frozen repository quality gates.

The exact refresh-head qualification and merge identities are intentionally recorded later in B005 canonical closeout evidence, not preclaimed here.
