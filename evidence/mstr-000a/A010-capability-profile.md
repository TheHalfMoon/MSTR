# A010 — Evidence-Derived CapabilityProfile Contract

**Task:** `MSTR-000A / A010`
**State:** `COMPLETE_CANONICAL`
**Canonical base:** `cdf5e89886919a05173a2921c03d213ee5992126`
**Authority:** contract/schema/fixture work only; no model execution or external effect.

## Objective

Freeze `mstr.capability-profile.v0`, the evidence-derived capability description consumed by WePLD routing and other harness policy. The contract records measured capability without converting vendor claims, model-card statements, or unevaluated expectations into project truth.

## Frozen fields

```text
reliable_context_budget
preferred_edit_arm
tool_call_reliability
localization_strength
planning_depth
recommended_verifier_cadence
max_repair_depth
fim_strength
shell_reliability
context_compaction_strength
```

Every capability field is explicitly `MEASURED` or `UNMEASURED`. A `MEASURED` field requires a typed value and at least one admissible evidence reference. An `UNMEASURED` field carries `value=null` and no field-level evidence references, preventing placeholder values from becoming routing authority.

## Evidence boundary

Admissible evidence source classes are exactly `MSTR_RUN`, `MSTR_RESULT`, `REPOSITORY_FIXTURE`, and `CANONICAL_DECISION`.

`VENDOR_CLAIM_ONLY` and other claim-only classes are intentionally invalid. Vendor/model-card material may motivate future measurement, but cannot by itself populate a measured capability field.

A real profile binds exact `model_id`, `model_revision`, `artifact_sha256`, `tokenizer_revision`, and `quantization_identity`. The fixture in this task is repository-owned synthetic evidence only and is explicitly not a real model capability claim.

## Validation

The task registers the schema in the repository-local schema registry and adds byte-identical design/runtime schemas, valid/invalid fixtures, contract tests, and offline validation regression coverage.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
REAL_CAPABILITY_MEASUREMENT = NONE
NETWORK_MODEL_OR_PROVIDER_CALL = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
A010_AUTHORITY = CAPABILITY_PROFILE_CONTRACT_AND_REPOSITORY_FIXTURES_ONLY
```

> This terminal state is a closeout candidate until the dedicated closeout PR is itself qualified, reviewed, mandatory-premerge verified, guarded-merged, and post-closeout verified on canonical `main`.

## Canonical Lifecycle Evidence

```text
CANONICAL_IMPLEMENTATION_BASE = cdf5e89886919a05173a2921c03d213ee5992126
ATOMIC_BUILDER_RUN = 33363386203 / SUCCESS
INITIAL_QUALIFICATION_RUN = 33363567728 / FAILURE / git diff --check trailing-space findings only
FINAL_IMPLEMENTATION_HEAD = 16aa467348d89cb4cbadc06314589cd51da346e9
FINAL_IMPLEMENTATION_TREE = b3660eb742b3aab3af755673ac2faa620081ad48
FINAL_EXACT_HEAD_QUALIFICATION = 33363643410 / SUCCESS
EXACT_HEAD_REVIEW = 5063628959 / COMMENTED / NO_BLOCKING_FINDING
UNRESOLVED_REVIEW_THREADS = 0
MANDATORY_PREMERGE = 33363854255 / SUCCESS
IMPLEMENTATION_PR = 104
IMPLEMENTATION_MERGE = ffbcbd9b43562302136f8fc2d1478ee4abfb180a
POST_MERGE_VERIFICATION_RUN = 33364067973 / SUCCESS
A010_STATE = COMPLETE_CANONICAL_CANDIDATE
A011_STATE = PENDING
```

No failed or superseded workflow run is represented as passing evidence. The initial qualification failure remains preserved as negative evidence and was superseded only by the whitespace-only hardening commit plus a fresh exact-head qualification. A011 remains independently gated and is not made complete by this closeout.
