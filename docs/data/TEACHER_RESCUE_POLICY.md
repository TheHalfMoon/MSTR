# MSTR Teacher Rescue Policy v0

**Task:** `B019`
**Contract:** `mstr.teacher-rescue-record.v0`
**Status:** IMPLEMENTATION_CANDIDATE

## Purpose

Teacher rescue is an optional, bounded frontier-rescue/reference path. A teacher is never a truth authority. B019 freezes evidence and admission semantics only; it does not call a teacher, execute a model, spend money, ingest a corpus, or authorize training.

## Trigger Boundary

A rescue record requires exact student failure evidence and an externally supplied `difficulty_record_identity`. B019 may bind that identity but MUST NOT create or calibrate difficulty; B020 owns checkpoint-relative difficulty calibration.

```text
STUDENT_FAILURE_EVIDENCE
+ DIFFICULTY_RECORD_IDENTITY
-> OPTIONAL_TEACHER_REFERENCE_OR_FUTURE_AUTHORIZED_RESCUE
-> CONCRETE_OUTPUT_PROVENANCE
-> CONCRETE_OUTPUT_RIGHTS
-> CONTAMINATION_CHECK
-> INDEPENDENT_EXECUTION_WHERE_REQUIRED
-> VERIFIER_HEALTH_IDENTITY
-> ADMIT | REJECT
```

## Required Evidence

Every record binds:

- exact task identity;
- exact student/checkpoint/harness/sampling failure identity;
- teacher identity and teacher terms identity;
- explicit cost/network/model-execution facts;
- every concrete teacher output identity;
- per-output provenance;
- per-output rights decision;
- contamination state;
- independent execution evidence for every execution-required output;
- verifier-health identity and independence state;
- deterministic admission decision and reasons.

Teacher identity or provider terms do not substitute for concrete-output rights. Output provenance/rights arrays must exactly cover all teacher outputs. Independent execution evidence must exactly cover outputs marked `execution_required=true`.

## Fail-Closed Admission

`ADMIT` requires all of the following:

```text
ALL_OUTPUT_PROVENANCE = COMPLETE
ALL_OUTPUT_RIGHTS = COMPATIBLE
CONTAMINATION = CLEAR
ALL_OUTPUT_CONTAMINATION = CLEAR
ALL_REQUIRED_EXECUTION = PASS + SANDBOXED
VERIFIER_HEALTH = HEALTHY
VERIFIER_INDEPENDENCE = INDEPENDENT
TEACHER_OUTPUT_SOLE_AUTHORITY = FALSE
ADMISSION_REASONS = []
```

Any unresolved/incompatible right, incomplete/unresolved provenance, contamination, missing execution evidence, failed execution, weak/unresolved verifier independence, or teacher-self-confirmation rejects clean-positive admission.

## External-Effect Authority

The contract may represent a future separately authorized teacher execution. It never creates that authority. If a record reports any paid cost, network use, or teacher-model execution, it MUST bind a non-null `external_effect_authority_identity` referencing already-canonical authority with the relevant scope/cost/network ceiling.

For `REFERENCE_ONLY`, paid cost, network use, and model execution must all be false/zero and the external-effect authority identity must be null.

```text
PAID_OR_API_TEACHER_AUTHORIZED_BY_B019 = FALSE
MODEL_EXECUTION_AUTHORIZED_BY_B019 = FALSE
NETWORK_TEACHER_CALL_AUTHORIZED_BY_B019 = FALSE
```

## Cross-Contract Authority

B019 consumes identities without stealing downstream authority:

```text
B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE
B022_VERIFIER_HEALTH_AUTHORITY = NONE
```

B022/B023 own verifier-health certification/evaluation semantics. B019 stores the health identity and fail-closed admission posture only.

## Non-Authorities

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE
B022_VERIFIER_HEALTH_AUTHORITY = NONE
```
