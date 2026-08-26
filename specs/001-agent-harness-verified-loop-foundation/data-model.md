# Data Model — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

## 1. LoopContract

Defines the bounded control system in which a builder operates.

Fields:
- `schema_version`
- `loop_id`
- `interaction_contract_id`
- `goal_policy`
- `tool_surface_id`
- `context_policy_id`
- `edit_policy_id`
- `verifier_policy_id`
- `stop_policy`
- `recovery_policy`
- `max_steps`
- `max_tool_calls`
- `max_repairs`
- `timeout_seconds`
- `effect_envelope_id`

Invariant: success is impossible without a verifier result satisfying `stop_policy.success`.

## 2. RunIdentity

Binds one execution to exact comparable inputs.

Fields:
- `run_id`
- `task_manifest_id`
- `repository_revision`
- `environment_manifest_id`
- `model_id`
- `model_revision`
- `artifact_sha256`
- `runtime_id`
- `interaction_contract_id`
- `loop_contract_id`
- `harness_profile_id`
- `verifier_manifest_id`
- `sampling_config`
- `seed`
- `timeout_seconds`
- `cache_state`
- `hardware_profile_id`

## 3. RunEvent

Append-oriented fact with monotonic ordering.

Fields:
- `schema_version`
- `run_id`
- `seq`
- `event_type`
- `logical_time`
- `step_id`
- `payload`
- `model_visible`
- `source`
- `sha256`

`seq` is strictly increasing. Event bytes are canonicalized before hashing.

Minimum `event_type` vocabulary:
- `run.started`
- `run.goal_admitted`
- `context.observed`
- `context.compacted`
- `plan.updated`
- `tool.requested`
- `tool.result`
- `edit.proposed`
- `edit.applied`
- `edit.rejected`
- `verifier.started`
- `verifier.result`
- `recovery.started`
- `recovery.result`
- `run.stop_proposed`
- `run.completed`
- `run.failed`
- `run.escalated`

## 4. AgentState

Derived working projection, never primary authority.

Fields:
- `goal`
- `acceptance_criteria`
- `non_goals`
- `constraints`
- `current_plan`
- `repo_map`
- `files_inspected`
- `changed_files`
- `commands_run`
- `verifier_results`
- `known_failures`
- `working_hypotheses`
- `remaining_work`
- `next_action`
- `derived_through_seq`

Invariant: any claim in `AgentState` must be derivable from events through `derived_through_seq`.

## 5. HarnessProfile

Defines one comparable scaffold arm.

Fields:
- `profile_id`
- `profile_kind`: `neutral_minimal | mstr_native | wepld_native | experimental`
- `loop_contract_id`
- `tool_surface_id`
- `context_policy_id`
- `edit_policy_id`
- `state_policy_id`
- `verifier_cadence`
- `runtime_dependencies`
- `resource_budget`

## 6. CapabilityProfile

Evidence-derived model capability description for WePLD/harness routing.

Fields:
- `profile_id`
- `model_artifact_identity`
- `reliable_context_budget`
- `preferred_edit_arm`
- `tool_call_reliability`
- `localization_strength`
- `planning_depth`
- `recommended_verifier_cadence`
- `max_repair_depth`
- `fim_strength`
- `shell_reliability`
- `context_compaction_strength`
- `evidence_refs`

No field may be populated from vendor claims alone.

## 7. EnvironmentManifest

Defines reproducible task execution world.

Fields:
- `environment_id`
- `repository_url`
- `repository_revision`
- `setup_recipe`
- `health_targets`
- `reset_recipe`
- `network_policy`
- `mount_policy`
- `secret_policy`
- `resource_limits`
- `setup_attempt_ceiling`
- `admission_status`
- `admission_evidence`

## 8. VerifierManifest

Fields:
- `verifier_id`
- `task_class`
- `required_commands`
- `hidden_paths`
- `protected_paths`
- `known_good_expectation`
- `known_bad_expectation`
- `shortcut_battery`
- `timeout_seconds`
- `success_rule`
- `result_schema_version`

## 9. DirectionTaskManifest

Fields:
- `task_id`
- `task_revision`
- `direction`
- `repository_revision`
- `environment_manifest_id`
- `verifier_manifest_id`
- `allowed_effects`
- `prohibited_effects`
- `timeout_seconds`
- `difficulty_tags`
- `task_family`
- `freshness/provenance`

`direction` should remain realistically terse; hidden acceptance logic belongs to the verifier surface.

## 10. TrajectoryManifest

Fields:
- `trajectory_id`
- `run_identity`
- `event_log_sha256`
- `terminal_class`
- `verifier_result_identity`
- `failure_classes`
- `recovery_count`
- `authority_violations`
- `contamination_status`
- `training_admission`
- `training_labels`
- `provenance`

Terminal classes:
- `VERIFIED_SUCCESS`
- `RECOVERED_SUCCESS`
- `FAILED_VALID`
- `TIMEOUT_VALID`
- `INVALID_ENVIRONMENT`
- `INVALID_VERIFIER`
- `CONTAMINATED`
- `LEAKAGE_DETECTED`
- `AUTHORITY_VIOLATION`

## 11. FailureRecord

Canonical failure taxonomy:
- `WRONG_LOCALIZATION`
- `BAD_ASSUMPTION`
- `STALE_FILE`
- `BAD_PATCH`
- `SYNTAX_ERROR`
- `TYPE_ERROR`
- `BUILD_FAILURE`
- `TEST_FAILURE`
- `DEPENDENCY_FAILURE`
- `TOOL_ERROR`
- `TIMEOUT`
- `INCOMPLETE_IMPLEMENTATION`
- `OVEREDIT`
- `REGRESSION`
- `FAKE_COMPLETION`
- `AUTHORITY_VIOLATION`
- `ENVIRONMENT_FAILURE`
- `VERIFIER_FAILURE`

## 12. ResearchCampaign

Frozen campaign-level authority.

Fields:
- `campaign_id`
- `baseline_commit`
- `mutable_surface`
- `frozen_evaluation_manifest`
- `frozen_verifier_manifest`
- `resource_budget`
- `cost_ceiling`
- `security_policy`
- `rights_policy`
- `keep_rule`
- `regression_rules`

## 13. ResearchExperiment

Fields:
- `experiment_id`
- `campaign_id`
- `parent_experiment_id`
- `code/config_commit`
- `hypothesis`
- `mutation_summary`
- `run_identities`
- `metrics`
- `status`: `keep | discard | crash | invalid`
- `decision_reason`
- `complexity_delta`

## 14. MetricRecord

Required primary/diagnostic metrics:
- `dvcr`
- `ttvc_seconds`
- `first_pass_accept_rate`
- `edit_survival_rate`
- `repair_success_rate`
- `tool_error_rate`
- `tool_calls_per_verified_completion`
- `tokens_per_verified_completion`
- `context_tokens_per_verified_completion`
- `harness_wall_time_overhead`
- `harness_memory_overhead`
- `q4_artifact_bytes` where applicable

A metric record must state denominator, exclusions, invalid-run count, and zero-solve behavior.
