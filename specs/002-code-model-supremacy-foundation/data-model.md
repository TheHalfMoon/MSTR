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
- external_effect_class
- required_authority_id?
- parallel_safe
- supersedes[]
- superseded_by[]
- closeout_rule
```

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
- generated_task
- generated_solutions[]
- generated_tests[]
- environment_identity
- execution_results[]
- verifier_health
- contamination_status
- difficulty_record
- admission_decision
```

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
- independent_execution_results[]
- verifier_health
- provenance
- admission_decision
```

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
- pre_fix_result
- post_fix_result
- mutation_strength
- protected_path_status
- verifier_health_id
- admission_decision
```

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

## 13. ResearchExperimentRecordV2

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
- budget
- results
- hard_gate_results
- promotion_decision
- decision_reason
- resource_cost
```

Fidelity:

```text
L0_CONTRACT_SMOKE
L1_CODE_PROXY
L2_EXECUTABLE_REPO
L3_DIRECTION_TO_DONE
L4_Q4_UNIVERSAL_LAPTOP
```

## 14. TrainingMethodCell

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

## 15. RepositoryHealthRecord

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

## 16. CandidatePoolDecision

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
