# B018 — Execution-Filtered Student Self-Alignment Contract

**Task:** `B018`
**Implementation PR:** #76
**Final implementation head:** `23c83ebae95ca3f0d893840e9d994b33712f124f`
**Canonical implementation merge:** `7e4996e92128e4e02ec6dbcf6ed29eed2b753838`
**State:** COMPLETE_CANONICAL
**Contract:** `mstr.self-alignment-generation.v0`
**Canonical main at execution:** `73b60aa9421f51be52560bbbca6e8dd46b77b6c9`
**Exact entry evidence:** run `33185451160` / job `98897160421` — SUCCESS

## Decision

B018 freezes the structural contract for execution-filtered student self-alignment without generating training data, executing a model, ingesting a corpus, or authorizing training.

The contract represents the canonical `SelfAlignmentGeneration` concepts from MSTR-000B:

- exact student model/checkpoint/harness/sampling identity;
- seed identity, provenance, rights decision, and contamination status;
- one generated task plus one-or-more generated solutions and tests;
- per-artifact provenance, rights, and contamination evidence;
- sandbox execution evidence for generated solutions and tests;
- independent verifier-health identity and health class;
- checkpoint-relative difficulty-record identity and class;
- a fail-closed `ADMIT` or `REJECT` decision with explicit rejection reasons.

## Fail-Closed Admission

`admission_decision=ADMIT` is structurally valid only when all of the following hold:

```text
SEED_PROVENANCE = COMPLETE
SEED_RIGHTS = COMPATIBLE
SEED_CONTAMINATION = CLEAR
EVERY_GENERATED_ARTIFACT_PROVENANCE = COMPLETE
EVERY_GENERATED_ARTIFACT_RIGHTS = COMPATIBLE
EVERY_GENERATED_ARTIFACT_CONTAMINATION = CLEAR
EVERY_SOLUTION_AND_TEST_EXECUTION = SANDBOXED_PASS
VERIFIER_HEALTH = HEALTHY
VERIFIER_INDEPENDENCE = INDEPENDENT
GENERATED_TESTS_SOLE_AUTHORITY = FALSE
OVERALL_CONTAMINATION = CLEAR
DIFFICULTY_CLASS != INVALID
ADMISSION_REASONS = []
```

`REJECT` requires at least one reason and deliberately preserves negative evidence states such as unresolved rights, broken verifier health, failed execution, or `INVALID` difficulty. The contract therefore does not make rejected research evidence unrepresentable.

## Per-Artifact Evidence Binding

The runtime schema preserves the canonical first-class evidence collections from `data-model.md`:

- `generated_artifact_provenance[]`
- `generated_artifact_rights_decisions[]`
- `execution_results[]`

Generated artifacts also carry local evidence copies so a record remains directly inspectable at the artifact boundary. Because JSON Schema alone cannot prove referential completeness across independent arrays, the offline B018 semantic validator fails closed unless the canonical arrays exactly cover the generated artifact identities and exactly match the nested provenance, rights, execution-result, and environment bindings.

Generated tasks are non-executable descriptions and reject an `execution_result`. Generated solutions and tests require execution evidence; `ADMIT` further requires that execution to be sandboxed and passing.
## Difficulty Boundary

B018 does not implement B020 or freeze its future calibration algorithm.

The enclosing `student_model_identity` carries the exact:

```text
model_id
checkpoint_id
harness_profile_id
sampling_identity
```

The nested difficulty record binds its evidence identity, one of the B014-frozen classes, and an explicit copy of the exact student model/checkpoint, harness profile, and sampling identity used by the generation. The offline B018 semantic validator rejects any mismatch between those embedded bindings and the enclosing generation identity.

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

B020 remains responsible for the detailed `DifficultyCalibrationRecord`, calibration procedure, refresh semantics, and frontier policy. B018 consumes only the record identity/class and exact identity binding. `INVALID` may be recorded on rejected evidence but cannot be admitted.
## Verifier-Health Boundary

B018 does not implement B022/B023.

It binds:

```text
verifier_health_record_identity
verifier_identity
health_class
independence
generated_tests_sole_authority
```

Only `HEALTHY + INDEPENDENT + generated_tests_sole_authority=false` can satisfy `ADMIT`. Detailed evaluator hashes, protected paths, mutation/shortcut checks, leakage analysis, disagreement handling, and stage eligibility remain owned by B022/B023.

This preserves the constitutional rule that student-generated tests cannot be the sole authority for their own solution.

## Runtime Registration

The design and runtime schemas must remain byte-identical:

```text
specs/002-code-model-supremacy-foundation/contracts/mstr-self-alignment-generation-v0.schema.json
schemas/mstr-self-alignment-generation-v0.schema.json
```

The contract is registered in both the offline schema registry and CLI schema-version auto-detection. Dedicated valid/invalid fixtures participate in `python -m mstr_qualify validate`.

## Canonical Entry Provenance

```text
ENTRY_GATE_TASK = B018
ENTRY_GATE_CANONICAL_MAIN = 73b60aa9421f51be52560bbbca6e8dd46b77b6c9
ENTRY_GATE_RUN = 33185451160
ENTRY_GATE_JOB = 98897160421
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

The successful entry gate also proved B014 `COMPLETE_CANONICAL`, B018 `PENDING`, no external authority requirement for B018, and B011 still `BLOCKED` with its required founder authority unsatisfied.

## Scope and Non-Authorities

B018 is contract/fixture work only. The valid fixture is synthetic repository-owned test data and does not represent an executed model generation.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

B011 remains separately blocked by its exact repository-required founder authority envelope.


## Canonical Field-Shape and Cross-Binding Repair

The contract exposes the canonical `SelfAlignmentGeneration` evidence surfaces as first-class fields rather than relying only on nested convenience copies:

- `generated_artifact_provenance[]`
- `generated_artifact_rights_decisions[]`
- `execution_results[]`

The offline validator fails closed unless those arrays exactly cover the generated artifact identities and exactly match the nested provenance, rights, execution result, and environment bindings. It also fails closed unless the embedded `difficulty_record` binds the exact student model/checkpoint, harness profile, and sampling identity used by the generation.

These are evidence bindings only. B018 does not perform difficulty calibration and does not create or certify verifier-health authority; those remain owned by their canonical tasks.

```text
B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE
B022_VERIFIER_HEALTH_AUTHORITY = NONE
B020_BINDING_SURFACE = difficulty_record_identity + exact student/harness/sampling identity
B022_BINDING_SURFACE = verifier_health_record_identity + verifier identity/health snapshot
```

## Canonical Implementation Closeout

The contract implementation was merged without widening authority, data scope, or external effects.

- implementation PR: `#76`
- final implementation head: `23c83ebae95ca3f0d893840e9d994b33712f124f`
- canonical implementation merge: `7e4996e92128e4e02ec6dbcf6ed29eed2b753838`
- exact-final-head qualification: run `33188891501` — SUCCESS
- independent adversarial review: run `33189093479` / job `98909650689` — SUCCESS
- mandatory pre-merge verification: run `33189307397` — SUCCESS
- post-merge implementation verification: run `33189815147` — SUCCESS

This closeout changes only canonical task/provenance state and regression assertions. It grants no model-weight access, model execution, paid compute, large-data ingestion, training, B020 difficulty-calibration authority, B022 verifier-health authority, or production release authority. B011 remains blocked.
