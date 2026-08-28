# MSTR-DATA-CONSTITUTION-v0

**Status:** B014 implementation candidate — not canonical until governed merge/closeout
**Contract:** `mstr.data-constitution.v0`
**Purpose:** define the minimum evidence and admission rules for data that may influence future MSTR training or clean-positive evaluation.

This constitution is deliberately fail-closed. It does not authorize dataset acquisition, private-user-data ingestion, model execution, paid/API teacher use, large-dataset ingestion, or weight-changing training.

## 1. Constitutional admission rule

A source being public, popular, technically useful, or machine-generated is not enough for admission.

Clean-positive admission requires all applicable gates:

```text
PROVENANCE_COMPLETE
AND RIGHTS_COMPATIBLE
AND CONTAMINATION_CLEAR
AND BENCHMARK_EXCLUSION_CLEAR
AND DEDUP_COMPLETE
AND VERIFIER_HEALTH_THRESHOLD_MET
AND TARGET_DISTRIBUTION_MANIFEST_BOUND
AND LANGUAGE_TARGET_POLICY_BOUND
AND TRAINING_EVAL_BOUNDARY_EXPLICIT
AND PRIVATE_USER_DATA_DEFAULT_REJECTION_ENFORCED
```

Missing, ambiguous, unresolved, or contradictory evidence is a rejection, not a soft pass.

## 2. Source classes

Potentially admissible classes:

```text
PUBLIC_OPEN_SOURCE_REPOSITORY
PUBLIC_DATASET_COMPATIBLE_RIGHTS
PUBLIC_DOCUMENTATION_COMPATIBLE_RIGHTS
REPOSITORY_OWNED_FIXTURE
SYNTHETIC_VERIFIED
STUDENT_GENERATED_VERIFIED
TEACHER_OUTPUT_VERIFIED
```

`allowed` means eligible to enter the evidence pipeline, not automatically admitted to training.

Constitutionally prohibited from clean-positive admission:

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

A future exception for private-user data requires a separate canonical policy and separate authority. B014 creates no such authority.

## 3. Private user data and telemetry

```text
PRIVATE_USER_REPOSITORY_DEFAULT_INGEST = FALSE
PRODUCTION_TRACE_DEFAULT_INGEST = FALSE
HIDDEN_TELEMETRY_ALLOWED = FALSE
DEFAULT_PRIVATE_USER_DATA_ADMISSION = REJECT
```

Private repositories, private patches, editor histories, prompts, production traces, or other user-derived material must never become training data merely because the runtime can observe them.

## 4. Canonical software-role taxonomy

B014 uses the exact software-role taxonomy frozen by the MSTR-000B plan:

```text
CODE
FIM
TEST
DIFF
BUILD_CI
TOOL_SHELL
ISSUE_DIRECTION
PR_REVIEW
SOFTWARE_EVOLUTION
REPAIR_RECOVERY
FEATURE_GREENFIELD
SECURITY
GENERAL_REASONING_REPLAY
```

Downstream schemas may add derived labels for analysis, but they may not silently replace or erase this constitutional role identity.

## 5. Target-distribution policy

B014 freezes the requirement for a target distribution without inventing one universal percentage mix before stage evidence exists.

```text
MODE = STAGE_SPECIFIC_MANIFEST
FIXED_PERCENTAGES_IN_B014 = FALSE
SOFTWARE_ROLE_DISTRIBUTION = REQUIRED
STAGE_SPECIFIC_MANIFEST = REQUIRED
EVIDENCE_SELECTED_MIX = REQUIRED
ROLE_COVERAGE_MAY_NOT_BE_SILENTLY_ZEROED = TRUE
```

Every training stage must bind an inspectable role-distribution manifest. Exact percentages may change only through stage-specific evidence and governance rather than marketing breadth or convenience.

## 6. Language target boundary

B014 intentionally does not choose language percentages or tiers. B015 owns the canonical language/tooling mix.

```text
LANGUAGE_TARGET_POLICY_MODE = EXTERNAL_CANONICAL_POLICY
REQUIRED_POLICY_TASK = B015
MUST_BE_BOUND_BEFORE_TRAINING_ADMISSION = TRUE
```

This satisfies the Data Constitution's language-mixture boundary without stealing B015 authority.

## 7. Provenance policy

Every source or generated artifact must bind to:

- source identity;
- source revision or immutable snapshot identity;
- acquisition/observation time as applicable;
- artifact lineage through transformations;
- transformation/generator identity when derived.

```text
UNRESOLVED_PROVENANCE_ADMISSION = REJECT
```

Filtering, deduplication, projection, or synthesis may not erase provenance.

## 8. Rights policy

Every source requires an explicit license/terms identity and a concrete rights decision for the intended use.

```text
UNRESOLVED_RIGHTS_ADMISSION = REJECT
INCOMPATIBLE_RIGHTS_ADMISSION = REJECT
TEACHER_TERMS_DO_NOT_SUBSTITUTE_OUTPUT_RIGHTS = TRUE
```

A repository license, dataset card, API provider name, or teacher identity is not itself sufficient evidence that every derived output may be trained on or redistributed.

## 9. Contamination policy

Applicable checks include:

- benchmark overlap;
- train/eval split leakage;
- future-history leakage in software evolution;
- hidden-test or hidden-answer exposure;
- cross-split near duplicates that invalidate evaluation independence.

```text
UNRESOLVED_CONTAMINATION_ADMISSION = REJECT
```

For software-evolution examples, future patches, later review outcomes, final tests, or other later events may not leak into model-visible context for an earlier step.

## 10. Deduplication policy

```text
EXACT_DEDUP = REQUIRED
NEAR_DUPLICATE_DETECTION = REQUIRED
CROSS_SPLIT_DEDUP = REQUIRED
PROVENANCE_AFTER_DEDUP = PRESERVED
```

The exact algorithm and thresholds may vary by downstream pipeline, but a pipeline may not claim clean separation without declaring them.

## 11. Benchmark exclusion policy

```text
BENCHMARK_EVAL_ITEMS_IN_TRAINING = PROHIBITED
HIDDEN_TESTS_IN_TRAINING = PROHIBITED
BENCHMARK_DERIVED_SOLUTION_LEAKAGE = PROHIBITED
NEAR_DUPLICATE_GUARD = REQUIRED
```

A public benchmark being downloadable does not make it eligible for training when it is retained as evaluation evidence.

## 12. Synthetic data policy

Synthetic data is admissible only after it becomes a traceable, independently checked artifact.

Required evidence:

- generator identity;
- generation provenance;
- rights decision;
- verifier evidence;
- contamination check.

```text
UNVERIFIED_SYNTHETIC_ADMISSION = REJECT
```

## 13. Student-generated self-alignment

Admission requires:

- seed provenance and rights;
- per-generated-artifact provenance and rights;
- sandbox execution where executable;
- independent verifier evidence;
- contamination check;
- difficulty record bound to exact student/harness/sampling identity.

```text
UNRESOLVED_STUDENT_GENERATED_ADMISSION = REJECT
```

Student-generated tests cannot be the sole authority proving their own solution correct.

## 14. Teacher policy

Teachers are bounded rescue/reference sources, never truth authorities.

Required for any concrete teacher output considered for training:

- teacher identity and terms identity;
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

Paid/API teacher use requires separate authority.

## 15. Difficulty policy

Difficulty is relative to the exact student and execution protocol.

Every material difficulty record identifies student/checkpoint, harness, sampling, and observed solve/failure evidence.

Frozen classes:

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

`INVALID` cannot become clean positive signal.

## 16. Verifier-health thresholds

B014 freezes admission posture while B022/B023 own detailed verifier-health implementation.

Clean positive:

```text
HEALTHY
```

Research/diagnostic use:

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

## 17. Training/evaluation boundary

A downstream stage must bind explicit identities for:

```text
TRAINING_ONLY_SET
EVALUATION_ONLY_SET
HELD_OUT_SET
BENCHMARK_EXCLUSION_POLICY
CROSS_SPLIT_DEDUP_POLICY
FUTURE_HISTORY_VISIBILITY
```

And must preserve:

```text
HIDDEN_TESTS_TRAINING_VISIBILITY = PROHIBITED
```

This boundary must be inspectable before training. A final patch, later review, hidden test, or held-out answer may not leak into an earlier training projection.

## 18. Stage-admission rule

No downstream stage may silently relax a constitutional gate.

Before admission the stage must prove:

```text
PROVENANCE_COMPLETE = TRUE
RIGHTS_COMPATIBLE = TRUE
CONTAMINATION_CLEAR = TRUE
BENCHMARK_EXCLUSION_CLEAR = TRUE
DEDUP_COMPLETE = TRUE
VERIFIER_HEALTH_THRESHOLD_MET = TRUE
TARGET_DISTRIBUTION_MANIFEST_BOUND = TRUE
LANGUAGE_TARGET_POLICY_BOUND = TRUE
TRAINING_EVAL_BOUNDARY_EXPLICIT = TRUE
PRIVATE_USER_DATA_DEFAULT_REJECTION_ENFORCED = TRUE
UNRESOLVED_EVIDENCE_ADMISSION = REJECT
```

A downstream task may impose stricter requirements. It may not weaken this constitution without an explicit successor constitution and canonical governance change.

## 19. Non-authorities

MSTR-DATA-CONSTITUTION-v0 does not authorize:

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

Machine-readable sources:

```text
schemas/mstr-data-constitution-v0.schema.json
specs/002-code-model-supremacy-foundation/contracts/mstr-data-constitution-v0.schema.json
```

Runtime and design-source files must remain byte-identical for B014 closeout.

The v0 schema freezes safety-critical posture as constants. Future flexibility requires an explicit versioned successor rather than an unreviewed optional field.
