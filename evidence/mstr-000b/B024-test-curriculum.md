# B024 — Test Generation Curriculum Evidence

**Task:** `B024`
**Implementation PR:** #135
**Final implementation head:** `fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2`
**Canonical implementation merge:** `138a2c2c1d86c050db79e3190ab24d7c1052fe44`
**State:** COMPLETE_CANONICAL
**Canonical entry main:** `1ffa71c94bda161ec7be7784de3a6a4be81570ad`
**Entry gate run:** `33535987808`
**Entry gate job:** `99950302502`

## Entry gate

Exact-main post-closeout validation proved B024 machine eligibility before material implementation.

```text
ENTRY_GATE_TASK = B024
ENTRY_GATE_CANONICAL_MAIN = 1ffa71c94bda161ec7be7784de3a6a4be81570ad
ENTRY_GATE_ELIGIBLE = true
TASK = B024
CANONICAL_MAIN = 1ffa71c94bda161ec7be7784de3a6a4be81570ad
TASK_DRIFT = clean
B023_STATE = COMPLETE_CANONICAL
B024_STATE = PENDING
B024_ELIGIBLE = true
B024_PREREQUISITE_B023 = satisfied
EXTERNAL_AUTHORITY_REQUIRED = false
B026 = blocked on B024
B011 = blocked on repository-specific external authority
```

Run `33535987808` also re-proved the B023 closeout merge identity, exact provenance, full repository quality gates, B026 dependency ordering, and the unchanged B011 authority boundary.

## Contract frozen by this implementation candidate

```text
SCHEMA_VERSION = mstr.test-generation-example.v0
TEST_CLASSES = REPRODUCTION,TARGETED_REGRESSION,BOUNDARY_ERROR,PROPERTY,METAMORPHIC
DEFAULT_PROOF = FAIL_BEFORE_PASS_AFTER
TASK_SPECIFIC_PROOF_REQUIRES_INDEPENDENT_ACCEPTANCE_EVIDENCE = true
TASK_SPECIFIC_ACCEPTANCE_PRESERVES_INDEPENDENT_EVIDENCE_ID = true
TASK_SPECIFIC_ACCEPTANCE_EXACT_CONTEXT_SHA256_BINDING = required
SAME_TEST_ARTIFACT_PRE_POST = required
SAME_ENVIRONMENT_PRE_POST = required
SAME_VERIFIER_MANIFEST_PRE_POST = required
FAIL_BEFORE_PASS_AFTER_DISTINCT_BASE_FIX_REVISIONS = required
ADMIT_REQUIRES_COMPATIBLE_RIGHTS = true
ADMIT_REQUIRES_CLEAR_CONTAMINATION = true
ADMIT_REQUIRES_COMPLETE_PROVENANCE = true
GENERATED_SOURCE_REQUIRES_GENERATOR_IDENTITY = true
PROVENANCE_LINEAGE_BINDS_EXACT_TEST_ARTIFACT_SHA256 = required
ADMIT_REQUIRES_HEALTHY_VERIFIER = true
VERIFIER_HEALTH_BINDING_TO_TASK_AND_EXECUTED_MANIFEST = required
VERIFIER_HEALTH_STAGE_IDENTITY = required
CLEAN_POSITIVE_STAGE_ELIGIBILITY = CLEAN_POSITIVE_ELIGIBLE
ADEQUATE_MUTATION_REQUIRES_NONZERO_EVIDENCE = true
NOT_APPLICABLE_MUTATION_REQUIRES_EXPLICIT_JUSTIFICATION = true
NOT_APPLICABLE_MUTATION_REQUIRES_ZERO_RUN = true
ADMIT_REQUIRES_PROTECTED_PATH_INTEGRITY = true
ANSWER_ENCODING = prohibited
TEST_WEAKENING = prohibited
```

Runtime and design-source schemas remain byte-identical. The valid repository-owned fixture demonstrates a reproduction/targeted/boundary test that fails on the base revision and passes on the fix revision with the exact same test artifact. The invalid fixture demonstrates that pass-before/pass-after cannot self-admit under the default repair proof.

## Scope boundary

This implementation intentionally does not:

- generate tests with any model;
- execute model inference or a teacher/API;
- execute an external verifier-health evaluator;
- ingest an external or large dataset;
- access model weights;
- mutate B024 canonical state or its task checkbox;
- authorize B026, B030, training, candidate-pool changes, or production release.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEST_GENERATION_EXECUTION = NONE
VERIFIER_EXECUTION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B024_AUTHORITY = TEST_GENERATION_CONTRACT_AND_FIXTURES_ONLY
```

## Completion boundary

This is implementation evidence only. B024 remains `PENDING` and its checkbox remains open until governed implementation merge, post-merge verification, and a separate canonical closeout.

## Independent review remediation

Codex independent review `5081151219` on reviewed commit `f052704cdb` identified three P1 fail-closed defects. This repair candidate addresses all three without changing task state or authority:

1. generated source classes now require a concrete generator identity, and clean-positive admission requires explicit `COMPLETE` provenance;
2. verifier health is represented as a canonical binding whose task identity and verifier manifest must match the exact executed proof;
3. `ADEQUATE` mutation strength now requires concrete evidence plus nonzero evaluated and killed mutation counts.

Regression tests reproduce each reviewed defect and require the repaired behavior. A new exact-head qualification and independent review are still required after this repair; the prior qualification and review do not transfer to the repaired head.

### Distinct-revision review remediation

The initial Codex review also identified that `FAIL_BEFORE_PASS_AFTER` could describe contradictory fail/pass outcomes on an identical code revision. This repair requires `base_revision != fix_revision` for that proof kind and adds a regression test that reproduces the rejected identical-revision case. `TASK_SPECIFIC_BEHAVIOR` is unchanged because this restriction is specific to claimed repair transitions.

### Stage-eligibility review remediation

Codex review `5081306167` on intermediate head `639c263b2c349f21dddc2539d46748f67e544a0e` identified that global `HEALTHY` verifier status could still be admitted when the referenced training stage was diagnostic-only or blocked. This repair mirrors the canonical trajectory binding: every verifier-health binding carries exact `stage_id` and `stage_admission_class`, and clean-positive `ADMIT` requires `CLEAN_POSITIVE_ELIGIBLE`. `PARTIAL`/`DISAGREEMENT` cannot claim clean-positive stage eligibility, while `BROKEN`/`LEAKED`/`TAMPERED` are stage-blocked. These fields record eligibility evidence only and grant no training or external-runtime authority.

### Patch-membership and integrity-evidence review remediation

Codex exact-head review on `2c57b8445c76b2c0b3efc59c4de5eda13bf3df53` identified two additional fail-closed defects. This repair requires every `test_path` to appear in `changed_paths`, preventing reuse of an unrelated unchanged test as generated evidence. It also requires concrete integrity-check evidence and checker-manifest identities, with the checked patch and test artifact hashes bound exactly to `generated_test_patch`. These bindings are evidence requirements only and grant no checker execution, model execution, or training authority.

```text
TEST_PATHS_SUBSET_OF_CHANGED_PATHS = required
INTEGRITY_CHECK_EVIDENCE = required
INTEGRITY_CHECKER_MANIFEST = required
INTEGRITY_EVIDENCE_PATCH_BINDING = required
INTEGRITY_EVIDENCE_TEST_ARTIFACT_BINDING = required
```

### Exact-head provenance, task-specific proof, and mutation N/A remediation

Codex exact-head review `5081833125` on `42debeb1b464ca8edcad8c647fd99d0749efc366` identified three further P1 fail-closed defects. This repair candidate addresses them without modifying the JSON Schema bytes, task state, or authority surface:

1. `generated_test_provenance.lineage_identity` must end with the exact `generated_test_patch.test_artifact_sha256`, so complete lineage from another generated test cannot authorize the current artifact;
2. `TASK_SPECIFIC_BEHAVIOR` preserves the concrete independent acceptance-evidence identity and appends a deterministic `binding-sha256` covering that evidence id plus exact task identity, fix revision, test artifact SHA-256, post-fix environment identity, verifier-manifest identity, and concrete post-fix execution-evidence identity; copying an unrelated evidence identifier or changing any bound context invalidates the record;
3. `NOT_APPLICABLE` mutation status is a true zero-run state: its `evidence_identity` must be `not-applicable:<explicit-justification>`, and both evaluated/killed counts must be exactly zero. Weak or executed mutation results cannot be relabeled N/A.

Regression tests reproduce all three fail-open cases. Runtime/design schema byte identity is intentionally preserved because these are cross-field semantic bindings enforced by the existing offline semantic validator, not new structural schema fields. A fresh exact-head qualification and independent review are required after publication of this repair; no earlier qualification or review transfers to the new head.


## Exact-head independent-evidence hardening

Fresh independent review proved that a task-specific acceptance identity must not reuse either pre-fix or post-fix execution evidence and merely recompute the context digest. Semantic admission now requires the independent identity to be distinct from both execution-evidence identities while preserving the existing exact-context SHA-256 binding.

```text
TASK_SPECIFIC_ACCEPTANCE_INDEPENDENT_FROM_EXECUTION_EVIDENCE = required
```

## Canonical Implementation Closeout

The B024 test-generation curriculum and acceptance contract were merged and independently verified on canonical main. This closeout records terminal task/provenance state only. It does not authorize test generation with a model, verifier execution, model execution, model-weight access, training, paid compute, external/private data ingestion, candidate-pool changes, or production release.

- implementation PR: `#135`
- final implementation head: `fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2`
- canonical implementation merge: `138a2c2c1d86c050db79e3190ab24d7c1052fe44`
- guarded final repair builder: run `33553919725` — SUCCESS
- exact-head qualification: run `33554572587` — SUCCESS
- exact-head independent review: CodeRabbit comment `5498547347` / run `e2805914-59c9-4314-99e2-04bcb3ed5892` — NO ACTIONABLE COMMENTS
- mandatory pre-merge verification: run `33559716801` — SUCCESS
- post-merge implementation verification: run `33560182387` — SUCCESS

The fresh Codex review request on the final head was service-blocked by the Codex code-review usage limit, so it was not represented as successful review evidence. The independent exact-head CodeRabbit review explicitly reviewed the exact base-to-head range and all 11 changed files. Its non-blocking future-risk note about authenticated producer provenance does not grant or imply runtime/training authority; authenticated evidence provenance remains a future consumer-side hardening requirement before any admission path may rely on such evidence.

This closeout changes only B024 canonical state/provenance, the canonical task ledger, and closeout regression coverage. The frozen B024 runtime/design schemas and semantic validator are unchanged by this closeout. B026 may become machine-eligible only because B022, B024, and B025 are now canonically complete. B011 remains separately blocked on repository-specific external authority.
