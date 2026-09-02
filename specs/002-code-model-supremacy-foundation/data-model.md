# Data Model — MSTR-000B

## 1. TaskNode

Machine-enforced repository work item.

```text
TaskNode
- task_id
- workstream_id
- title
- canonical_state
- prerequisites[]
- outputs[]
- evidence_outputs[]
- candidate_dependent
- candidate_pool_requirement_id?
- external_effect_class
- required_authority_id?
- parallel_safe
- supersedes[]
- superseded_by[]
- closeout_rule
```

### Authority mapping

`candidate_dependent=true` does **not** by itself create external-effect authority. It MUST instead carry a non-null `candidate_pool_requirement_id` identifying the canonical candidate pool/evidence prerequisite that must be satisfied before execution.

`required_authority_id` is fail-closed according to `external_effect_class`:

```text
NO_EXTERNAL_EFFECT                -> required_authority_id MAY be null
PUBLIC_METADATA_READ              -> required_authority_id MAY be null when the canonical task itself permits the read
TOKENIZER_METADATA_OR_SMALL_FILES -> required_authority_id MAY be null when the canonical task itself permits the read and no model-weight file is accessed

MODEL_WEIGHT_ACCESS               -> required_authority_id MUST be non-null
GATED_TERMS_ACCEPTANCE             -> required_authority_id MUST be non-null
PAID_MODEL_API_EXECUTION           -> required_authority_id MUST be non-null
PAID_COMPUTE                       -> required_authority_id MUST be non-null
RENTED_COMPUTE                     -> required_authority_id MUST be non-null
LARGE_DATASET_INGESTION            -> required_authority_id MUST be non-null
WEIGHT_CHANGING_TRAINING           -> required_authority_id MUST be non-null
LONG_TRAINING                      -> required_authority_id MUST be non-null
LARGE_SCALE_RL                     -> required_authority_id MUST be non-null
PRODUCTION_RELEASE                 -> required_authority_id MUST be non-null
```

B002 contract fixtures MUST include every authority-gated class with `required_authority_id` missing and MUST produce `eligible=false`. Candidate-dependent fixtures with a missing `candidate_pool_requirement_id` MUST also produce `eligible=false` even when `external_effect_class=NO_EXTERNAL_EFFECT`.

## 2. TaskEligibilityResult

```text
TaskEligibilityResult
- task_id
- canonical_main
- eligible
- prerequisite_results[]
- authority_result
- supersession_result
- state_consistency_result
- candidate_pool_result
- reasons[]
```

`eligible=false` is fail-closed. The validator does not change repository state.

## 3. BackboneCandidateV2

Extends existing candidate evidence conceptually without requiring immediate migration of historical records.

```text
BackboneCandidateV2
- candidate_id
- model_id
- immutable_revision
- provenance_class
- specialization_class
- parameter_count
- context_length
- tokenizer_identity
- rights_record
- source_artifacts[]
- architecture
- fim_capabilities
- training_compatibility[]
- runtime_compatibility[]
- quantization_compatibility[]
- admission_state
- rejection_reasons[]
```

`specialization_class` may include `GENERAL_BASE`, `CODE_BASE`, `CODE_CONTROL`, `REFERENCE_ONLY`.

## 4. TokenizerEconomicsRecord

```text
TokenizerEconomicsRecord
- candidate_id
- tokenizer_id
- tokenizer_revision
- corpus_manifest_id
- total_bytes
- total_tokens
- bytes_per_token
- per_language[]
- diff_tokens
- stacktrace_tokens
- tool_json_tokens
- path_tokens
- fragmentation_metrics
```

## 5. DataConstitution

```text
DataConstitution
- constitution_id
- version
- allowed_source_classes[]
- prohibited_source_classes[]
- software_role_taxonomy[]
- language_target_policy
- provenance_policy
- rights_policy
- contamination_policy
- dedup_policy
- benchmark_exclusion_policy
- synthetic_policy
- student_generated_policy
- teacher_policy
- difficulty_policy
- verifier_health_thresholds
- stage_admission_rules
```

## 6. SoftwareEvolutionRecord

```text
SoftwareEvolutionRecord
- record_id
- repository_identity
- base_revision
- direction_identity
- issue_pr_identity?
- visible_context_manifest
- change_events[]
- test_ci_events[]
- review_events[]
- recovery_events[]
- final_revision
- final_verifier_identity
- future_history_boundary
- provenance
- rights
- contamination_status
```

Any training projection MUST declare which events were model-visible at the target step.

## 7. SelfAlignmentGeneration

```text
SelfAlignmentGeneration
- generation_id
- student_model_identity
- seed_identity
- seed_provenance
- seed_rights_decision
- generated_task
- generated_solutions[]
- generated_tests[]
- generated_artifact_provenance[]
- generated_artifact_rights_decisions[]
- environment_identity
- execution_results[]
- verifier_health
- contamination_status
- difficulty_record
- admission_decision
- admission_reasons[]
```

`admission_decision=ADMIT` is valid only when seed provenance is complete, seed rights are compatible, every generated artifact has bound provenance and compatible rights, contamination is clear, execution evidence is valid, verifier health satisfies the stage threshold, and the difficulty record matches the exact student/harness/sampling identity. Missing or unresolved evidence fails closed.

## 8. TeacherRescueRecord

```text
TeacherRescueRecord
- rescue_id
- task_identity
- student_failure_evidence
- teacher_identity
- teacher_terms_identity
- cost_record
- teacher_outputs[]
- output_provenance[]
- output_rights_decisions[]
- contamination_status
- independent_execution_results[]
- verifier_health
- admission_decision
- admission_reasons[]
```

A teacher's identity or terms record is not an output-rights decision. `ADMIT` requires compatible rights for every concrete output, clear contamination status, exact provenance, independent execution, and stage-eligible verifier health. Any unresolved right, provenance, or contamination state fails closed.

## 9. DifficultyCalibrationRecord

```text
DifficultyCalibrationRecord
- task_or_family_id
- student_model_identity
- harness_profile_id
- sampling_identity
- attempt_count
- success_count
- estimated_solve_probability
- structural_features
- failure_distribution
- difficulty_class
- calibration_time
```

Difficulty classes:

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

## 10. VerifierHealthRecord

```text
VerifierHealthRecord
- verifier_health_id
- task_identity
- verifier_manifest_id
- evaluator_hashes[]
- protected_paths[]
- reference_oracle_status
- noop_fail_status
- known_bad_fail_status
- mutation_results[]
- generated_test_independence
- leakage_checks[]
- disagreement_signals[]
- health_class
- training_stage_eligibility[]
```

Health classes:

```text
HEALTHY
PARTIAL
DISAGREEMENT
BROKEN
LEAKED
TAMPERED
```

## 11. TestGenerationExample

```text
TestGenerationExample
- example_id
- task_identity
- base_revision
- behavior_contract
- generated_test_patch
- generated_test_provenance
- generated_test_rights_decision
- contamination_status
- pre_fix_result
- post_fix_result
- mutation_strength
- protected_path_status
- verifier_health_id
- admission_decision
- admission_reasons[]
```

`ADMIT` requires complete provenance, compatible rights, clear contamination status, healthy-enough verifier identity, protected-path integrity, and the required pre-fix-fail/post-fix-pass or other task-specific behavioral proof. Passing tests alone is insufficient.

## 12. GreenfieldTaskManifest

```text
GreenfieldTaskManifest
- task_id
- complexity_band
- direction
- allowed_languages[]
- environment_identity
- hidden_behavior_manifest
- resource_budget
- verifier_manifest_id
- contamination_boundary
- provenance
```

Complexity bands:

```text
G0_FUNCTION
G1_MODULE_TESTS
G2_COMPONENT_FILE
G3_MULTI_FILE_FEATURE
G4_BOUNDED_PROGRAM
G5_MULTI_ROUND_EVOLUTION
```

## 13. MaterialResultIdentity

Every material research result serializes exact identity rather than hiding it in a generic result blob.

```text
MaterialResultIdentity
- result_id
- model_id_or_na
- model_revision_or_na
- model_artifact_sha256_or_na
- tokenizer_id_or_na
- tokenizer_revision_or_na
- quantization_method_or_na
- quantizer_tool_revision_or_na
- runtime_id_or_na
- runtime_version_or_commit_or_na
- runtime_build_flags_or_na
- os_identity_or_na
- cpu_identity_or_na
- total_ram_bytes_or_na
- thread_count_or_na
- acceleration_backend_or_na
- context_length_or_na
- cache_state_or_na
- interaction_contract_version_or_na
- loop_contract_version_or_na
- harness_profile_id_or_na
- task_manifest_id
- verifier_manifest_id
- verifier_health_id_or_na
- sampling_config_id_or_na
- data_identity_or_na
- difficulty_identity_or_na
- evidence_kind
- seed_or_na
- result_classification
- metrics
- wall_time_seconds_or_na
- resource_cost
- paid_cost_usd
- invalidation_reason_or_na
```

Fields that do not apply MUST carry an explicit `N/A`/not-applicable value rather than disappearing. A material comparison with a missing required identity is invalid.

## 14. ResearchExperimentRecordV2

```text
ResearchExperimentRecordV2
- experiment_id
- campaign_id
- parent_identity
- hypothesis
- mutable_surface
- mutation_identity
- frozen_evaluation_identity
- fidelity_level
- predecessor_promotion
- budget
- material_results[] : MaterialResultIdentity
- hard_gate_results
- promotion_decision
- decision_reason
- aggregate_resource_cost
- external_effect_authority
```

Fidelity:

```text
L0_CONTRACT_SMOKE
L1_CODE_PROXY
L2_EXECUTABLE_REPO
L3_DIRECTION_TO_DONE
L4_Q4_UNIVERSAL_LAPTOP
```

`predecessor_promotion` is `null` only at L0. L1-L4 MUST bind an immediate-predecessor `PROMOTE` record from the same campaign and frozen evaluation identity, including the promoted result identity and immutable evidence identity; the current `parent_identity` MUST equal that promoted result identity. Material-result count and aggregate wall-time/paid-cost MUST remain within the predeclared budget. Missing or contradictory predecessor/budget evidence fails closed. `PROMOTE` also requires exact machine-readable gate coverage for the selected fidelity level. Training evidence requires concrete data and checkpoint-relative difficulty identities. Any external-effect resource class or cost requires an immutable reference to a separately canonical authority record plus scope and ceiling checks; the research record never creates that authority.

## 15. TrainingMethodCell

```text
TrainingMethodCell
- cell_id
- backbone_identity
- method
- precision
- lora_rank?
- rslora?
- quantization?
- dataset_manifest_id
- token_update_budget
- seed_policy
- environment_identity
- eval_identity
- export_recipe
- q4_recipe
- status
```

## 16. Q4PromotionRecord

A checkpoint may become a parent of a later material weight-changing stage only through a successful Q4 promotion record.

```text
Q4PromotionRecord
- source_training_run_id
- source_checkpoint_sha256
- merged_master_sha256
- export_tool_id
- export_tool_revision
- export_recipe_hash
- quantizer_tool_id
- quantizer_tool_revision
- quantization_recipe_hash
- canonical_q4_artifact_sha256
- artifact_integrity_status
- q4_regression_manifest_id
- q4_regression_result
- universal_laptop_gate_result
- promotion_status
- rejection_reasons[]
```

`promotion_status=PROMOTED` is fail-closed unless merged-master export succeeds, both master and Q4 artifact hashes are verified, export/quantization tool revisions and recipes are pinned, required Q4 regressions pass, and the applicable universal-laptop hard gate passes. A BF16/FP16/master-only gain cannot become the parent checkpoint of the next material stage.

## 17. RepositoryHealthRecord

```text
RepositoryHealthRecord
- sequence_id
- repository_identity
- before_revision
- after_revision
- task_count
- duplication_delta?
- dead_code_delta?
- lint_type_delta?
- complexity_delta?
- dependency_delta?
- test_health_delta?
- architecture_violation_delta?
- rework_churn
- normalized_health_class
```

## 18. CandidatePoolDecision

```text
CandidatePoolDecision
- decision_id
- candidate_records[]
- excluded_candidates[]
- product_hard_gates
- comparability_manifest
- stable_pool
- unresolved_cells[]
```

A pool is not stable when one candidate has materially weaker/missing evidence that could change the comparison outcome.

### B026 canonical research resolution

`mstr.research-experiment.v2` is fail-closed against self-attested promotion or authority. `governing_task_id` and `predecessor_promotion.experiment_id` derive the predecessor registry path `artifacts/results/research/<governing_task_id>/registry/<experiment_id>.json`; `experiment_record_sha256` binds the exact bytes. The resolved record must itself validate, belong to the same campaign/task/evaluator lineage, be the immediately preceding fidelity level, have decision `PROMOTE`, and expose the exact promoted result consumed as the current parent.

Every experiment explicitly declares every governed external-effect class as `true` or `false`. Any true class requires `external_effect_authority`, whose path is derived only as `artifacts/authorities/<authority_id>.json`. The experiment stores only `authority_id` plus the canonical file SHA-256. Scope, campaign binding, strongest effect, and resource ceilings are derived from the resolved `AUTHORIZED_CANONICAL` artifact and are never copied into a mutable experiment authority surface.

`PROMOTE` binds `promoted_result_id_or_na` to a material result. Per-level identity gates have concrete semantic requirements. L4 additionally requires exact model/Q4 artifact, tokenizer, quantizer, runtime/build, OS/CPU/RAM/thread/backend/context/cache identities and binds both `q4_artifact_identity` and `q4_promotion_record_promoted` gate evidence to the exact promoted artifact/Q4 record. Aggregate paid cost must equal the sum of per-result paid costs before budget or authority ceilings are evaluated.
