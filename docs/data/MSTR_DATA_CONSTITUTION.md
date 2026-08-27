# MSTR-DATA-CONSTITUTION-v0

**Status:** B014 implementation candidate — not canonical until governed merge/closeout  
**Contract:** `mstr.data-constitution.v0`  
**Purpose:** define the minimum evidence and admission rules for data that may influence future MSTR training or clean-positive evaluation.

This constitution is deliberately fail-closed. It does not authorize dataset acquisition, private-user-data ingestion, model execution, paid/API teacher use, large-dataset ingestion, or weight-changing training.

## 1. Constitutional rule

A source being public, popular, technically useful, or machine-generated is **not** enough for admission.

A training/evaluation artifact is eligible for clean-positive admission only when all applicable gates are satisfied:

```text
PROVENANCE_COMPLETE
AND RIGHTS_COMPATIBLE
AND CONTAMINATION_CLEAR
AND BENCHMARK_EXCLUSION_CLEAR
AND DEDUP_COMPLETE
AND VERIFIER_HEALTH_THRESHOLD_MET
AND LANGUAGE_TARGET_POLICY_BOUND
AND TRAINING_EVAL_BOUNDARY_EXPLICIT
AND PRIVATE_USER_DATA_DEFAULT_REJECTION_ENFORCED
```

Missing, ambiguous, unresolved, or contradictory evidence is a rejection, not a soft pass.

## 2. Allowed source classes

The constitution recognizes only these source classes as potentially admissible:

```text
PUBLIC_OPEN_SOURCE_REPOSITORY
PUBLIC_DATASET_COMPATIBLE_RIGHTS
PUBLIC_DOCUMENTATION_COMPATIBLE_RIGHTS
REPOSITORY_OWNED_FIXTURE
SYNTHETIC_VERIFIED
STUDENT_GENERATED_VERIFIED
TEACHER_OUTPUT_VERIFIED
```

`allowed` means **eligible to enter the evidence pipeline**, not automatically admitted to training.

Every artifact still requires its own applicable provenance, rights, contamination, dedup, benchmark-exclusion, verifier-health, and stage-admission evidence.

## 3. Prohibited source classes

The following classes are constitutionally prohibited from clean-positive training admission:

```text
PRIVATE_USER_REPOSITORY
PRODUCTION_TRACE
UNKNOWN_PROVENANCE
UNRESOLVED_RIGHTS
BENCHMARK_EVALUATION_ITEM
FUTURE_HISTORY_LEAKAGE
UNVERIFIED_SYNTHETIC
UNVERIFIED_TEACHER_OUTPUT
```

A future exception for private-user data requires a separate canonical policy and separate authority. B014 itself creates no such authority.

## 4. Private user data and telemetry

MSTR defaults to privacy-preserving local use:

```text
PRIVATE_USER_REPOSITORY_DEFAULT_INGEST = FALSE
PRODUCTION_TRACE_DEFAULT_INGEST = FALSE
HIDDEN_TELEMETRY_ALLOWED = FALSE
DEFAULT_PRIVATE_USER_DATA_ADMISSION = REJECT
```

Private repositories, private patches, editor histories, prompts, production traces, or other user-derived material must never become training data merely because the runtime can observe them.

No hidden telemetry may be used to create a future training corpus.

## 5. Software-role taxonomy

MSTR data must model software building rather than collapse into undifferentiated token streams. The v0 taxonomy is:

```text
STATIC_CODE
SOFTWARE_EVOLUTION
LOCALIZATION
EDIT_PATCH
REVIEW_REPAIR
FAILURE_RECOVERY
TEST_GENERATION
GREENFIELD_FUNCTION
GREENFIELD_MODULE
MULTI_FILE_FEATURE
BOUNDED_PROGRAM
TOOL_USE
BUILD_CONFIG_CI
```

At minimum, future admitted mixtures must preserve meaningful coverage of static code, software evolution, test generation, multi-file feature work, and tool use.

The taxonomy does not prescribe percentages. Exact language/tooling distribution belongs to B015.

## 6. Language target boundary

B014 intentionally does **not** choose language percentages or tiers.

The Data Constitution requires a separately canonical B015 language-target policy before training admission:

```text
LANGUAGE_TARGET_POLICY_MODE = EXTERNAL_CANONICAL_POLICY
REQUIRED_POLICY_TASK = B015
MUST_BE_BOUND_BEFORE_TRAINING_ADMISSION = TRUE
```

This prevents B014 from stealing B015 authority while still making language-mixture binding mandatory.

## 7. Provenance policy

Every source or generated artifact must bind to:

- source identity;
- source revision or immutable snapshot identity;
- acquisition/observation time as applicable;
- artifact lineage from source through transformations;
- transformation/generator identity when derived.

```text
UNRESOLVED_PROVENANCE_ADMISSION = REJECT
```

Derived artifacts may not erase provenance during filtering, deduplication, projection, or synthesis.

## 8. Rights policy

Every source requires an explicit license/terms identity and a concrete rights decision for the intended use.

A repository license, dataset card, API provider name, or teacher identity is not itself sufficient evidence that every derived output may be trained on or redistributed.

```text
UNRESOLVED_RIGHTS_ADMISSION = REJECT
INCOMPATIBLE_RIGHTS_ADMISSION = REJECT
TEACHER_TERMS_DO_NOT_SUBSTITUTE_OUTPUT_RIGHTS = TRUE
```

Future data pipelines must preserve the evidence used to reach each rights decision.

## 9. Contamination policy

Every candidate training/evaluation unit must be checked for applicable contamination, including:

- benchmark overlap;
- train/eval split leakage;
- future-history leakage in software evolution records;
- hidden-test or hidden-answer exposure;
- cross-split near duplicates that invalidate evaluation independence.

```text
UNRESOLVED_CONTAMINATION_ADMISSION = REJECT
```

For software-evolution examples, future patches, later review outcomes, final tests, or other later events may not leak into model-visible context for an earlier step.

## 10. Deduplication policy

Dedup is an evidence-preserving transformation, not a license to throw away source identity.

Required controls:

```text
EXACT_DEDUP = REQUIRED
NEAR_DUPLICATE_DETECTION = REQUIRED
CROSS_SPLIT_DEDUP = REQUIRED
PROVENANCE_AFTER_DEDUP = PRESERVED
```

The exact algorithm and thresholds may vary by downstream pipeline, but a pipeline may not claim clean separation without declaring them.

## 11. Benchmark exclusion policy

MSTR must not train on the answers it later presents as evaluation evidence.

```text
BENCHMARK_EVAL_ITEMS_IN_TRAINING = PROHIBITED
HIDDEN_TESTS_IN_TRAINING = PROHIBITED
BENCHMARK_DERIVED_SOLUTION_LEAKAGE = PROHIBITED
NEAR_DUPLICATE_GUARD = REQUIRED
```

A public benchmark being openly downloadable does not make it eligible for training if it is retained as an evaluation surface.

## 12. Synthetic data policy

Synthetic data is admissible only after it becomes a traceable, independently checked artifact.

Required evidence includes:

- generator identity;
- generation provenance;
- rights decision;
- verifier evidence;
- contamination check.

```text
UNVERIFIED_SYNTHETIC_ADMISSION = REJECT
```

A generated example is not positive training signal merely because a model produced it confidently.

## 13. Student-generated self-alignment policy

Student self-alignment must remain execution-filtered and evidence-bound.

Required for admission:

- seed provenance;
- seed rights decision;
- per-generated-artifact provenance;
- per-generated-artifact rights decision;
- sandbox execution where the task is executable;
- independent verifier evidence;
- contamination check;
- difficulty record tied to the exact student/harness/sampling identity.

```text
UNRESOLVED_STUDENT_GENERATED_ADMISSION = REJECT
```

Student-generated tests cannot be the sole authority proving their own solution correct.

## 14. Teacher policy

Teachers are bounded rescue/reference sources, not truth authorities.

Required for any concrete teacher output considered for training:

- teacher identity;
- teacher terms identity;
- output provenance;
- output-specific rights decision;
- independent execution/verification where applicable;
- verifier-health evidence;
- contamination check.

```text
TEACHER_IDENTITY_IS_TRUTH = FALSE
UNRESOLVED_TEACHER_OUTPUT_ADMISSION = REJECT
PAID_OR_API_TEACHER_AUTHORIZED_BY_B014 = FALSE
```

Paid/API teacher use requires separate authority outside this constitution.

## 15. Difficulty policy

Difficulty is relative to the exact student and execution protocol, not an eternal label on a task.

Every material difficulty record must identify:

- student/checkpoint identity;
- harness profile;
- sampling identity;
- observed solve/failure evidence.

The frozen classes are:

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

`INVALID` examples cannot become clean positive signal.

## 16. Verifier-health thresholds

B014 freezes the admission posture while B022/B023 own the detailed verifier-health contract and implementation.

For **clean positive training admission**:

```text
ALLOWED = HEALTHY
```

For **research/diagnostic use only**:

```text
HEALTHY
PARTIAL
DISAGREEMENT
```

Blocked from clean-positive admission:

```text
BROKEN
LEAKED
TAMPERED
```

This prevents a weak or compromised verifier from silently manufacturing positive labels.

## 17. Stage-admission rule

No downstream stage may silently relax a constitutional gate.

An example or corpus slice may be admitted only after the stage can prove all required checks and identify the canonical policies/contracts used for them.

```text
UNRESOLVED_EVIDENCE_ADMISSION = REJECT
```

A downstream task may impose stricter requirements. It may not weaken this constitution without an explicit successor constitution and canonical governance change.

## 18. Training/evaluation boundary

The training/evaluation boundary must be explicit and inspectable before training.

At minimum, downstream manifests must be able to prove:

- what is training-only;
- what is evaluation-only;
- what is held out/private;
- what dedup/contamination checks connect the splits;
- what benchmark families are excluded from training;
- what future-history information is hidden at each software-evolution step.

## 19. Non-authorities

MSTR-DATA-CONSTITUTION-v0 does **not** authorize:

```text
PRIVATE_USER_DATA_INGESTION
PRODUCTION_TRACE_INGESTION
LARGE_DATASET_INGESTION
PAID_TEACHER_OR_MODEL_API_USE
MODEL_WEIGHT_ACCESS
MODEL_EXECUTION
WEIGHT_CHANGING_TRAINING
LARGE_SCALE_RL
PRODUCTION_RELEASE
```

The constitution is a gate. It is never an authority grant.

## 20. Machine contract

The machine-readable source of this policy is:

```text
schemas/mstr-data-constitution-v0.schema.json
specs/002-code-model-supremacy-foundation/contracts/mstr-data-constitution-v0.schema.json
```

The runtime and design-source files must remain byte-identical for B014 closeout.

The v0 schema intentionally freezes safety-critical boolean/enum posture as constants. Future flexibility requires an explicit versioned successor rather than an unreviewed optional field.
