# B025 — Greenfield / Feature / Synthesis Curriculum Evidence

**Task:** `B025`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `cd3e3ba39c0e83548748275d08b7a3d0d2e6b15b`
**Entry gate run:** `33246944029`
**Entry gate job:** `99085947153`

## Entry gate

Exact-main machine validation completed successfully before material B025 execution.

```text
TASK = B025
CANONICAL_MAIN = cd3e3ba39c0e83548748275d08b7a3d0d2e6b15b
TASK_DRIFT = clean
TASKS_CHECKED = 34
B025_STATE = PENDING
B025_ELIGIBLE = true
B025_REASONS = []
EXTERNAL_AUTHORITY_REQUIRED = false
FRONTIER_PENDING_ELIGIBLE = B025,B028
```

The same run proved B011 remained blocked by missing repository-specific external authority, B023 remained blocked by A006/A014, and no terminal task was reopened.

## Contract frozen by this implementation candidate

```text
SCHEMA_VERSION = mstr.greenfield-task.v0
COMPLEXITY_BANDS = G0_FUNCTION,G1_MODULE_TESTS,G2_COMPONENT_FILE,G3_MULTI_FILE_FEATURE,G4_BOUNDED_PROGRAM,G5_MULTI_ROUND_EVOLUTION
SYNTHESIS_METHODS = FEATURE_TREE_SYNTHESIS,SEMANTIC_SYNTHESIS
SYNTHESIS_DEFAULT = EXPERIMENTAL_PROPOSAL_ONLY
CURRICULUM_ELIGIBLE_REQUIRES_COMPATIBLE_RIGHTS = true
CURRICULUM_ELIGIBLE_REQUIRES_CLEAR_CONTAMINATION = true
HIDDEN_BEHAVIOR_MODEL_VISIBILITY = prohibited
VERIFIER_HEALTH_REQUIREMENT = HEALTHY
UNRESTRICTED_NETWORK_POLICY = prohibited
```

Runtime and design-source schemas are required to remain byte-identical. The valid fixture is repository-owned and performs no model or external execution. The invalid fixture proves that unverified feature-tree synthesis cannot self-admit as curriculum-eligible.

## Scope boundary

This implementation intentionally does not:

- execute feature-tree or semantic synthesis;
- implement B023 verifier-health evaluation;
- implement B024 test-generation curriculum;
- ingest any external dataset;
- access model weights or execute a model;
- use a teacher/API or paid compute;
- mutate task canonical state or mark B025 complete before post-merge closeout.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
VERIFIER_HEALTH_EVALUATOR_EXECUTION = NONE
SYNTHESIS_EXECUTION = NONE
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
B025_AUTHORITY = GREENFIELD_FEATURE_CURRICULUM_CONTRACT_AND_FIXTURES_ONLY
```
