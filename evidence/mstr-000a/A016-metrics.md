# A016 — DVCR / TTVC and Diagnostic Metric Computation

**Task:** `A016`
**State:** IMPLEMENTATION_CANDIDATE
**Canonical base:** `907ab88722223cf53379bc98935f0641536a6907`
**Feature branch:** `feat/000a-a016-diagnostic-metrics`

## Scope

A016 implements the model-independent metric computation required before the
Direction-to-Done harness tournament and trajectory convergence work. The module
consumes already-observed run-level counts and timings only; it performs no model
execution, repository mutation, network access, artifact acquisition, training,
or external evaluation.

Implemented mandatory metrics:

```text
DVCR = verified eligible completions / eligible direction attempts
TTVC = median seconds among independently verified completions only
FPAR = first implementation accepted / eligible direction attempts
ESR = surviving edit units / proposed edit units across eligible attempts
RSR = successful recoveries / eligible attempts that entered repair
TER = failed/invalid tool actions / all tool actions in eligible attempts
TOOL_CALLS_PER_VERIFIED_COMPLETION = failure-inclusive tool calls / verified completions
TOKENS_PER_VERIFIED_COMPLETION = failure-inclusive tokens / verified completions
CONTEXT_TOKENS_PER_VERIFIED_COMPLETION = failure-inclusive context tokens / verified completions
HARNESS_WALL_TIME_OVERHEAD = arithmetic mean seconds across eligible attempts
HARNESS_MEMORY_OVERHEAD = arithmetic mean bytes across eligible attempts
```

`q4_artifact_bytes` may be attached when applicable, but A016 does not execute or
qualify Q4 artifacts.

## Denominator and exclusion contract

Every `MetricRecord` exposes explicit denominator counts for DVCR, TTVC, FPAR,
ESR, RSR, TER, per-verified-completion efficiency metrics, and harness overhead.
It also records:

```text
attempt_count
eligible_attempt_count
verified_completion_count
excluded_run_count
invalid_run_count
exclusions[] with deterministic reason counts
invalid_reasons[] with deterministic reason counts
zero_solve
zero_solve_behavior
```

`excluded` and `invalid` attempts remain represented as evidence but do not enter
score denominators. An aggregate containing no eligible attempts reports DVCR and
other eligibility-dependent rates as `null`, not as a fabricated zero-percent
performance result.

## Zero-solve behavior

When eligible attempts exist but none reaches independent verified completion:

```text
DVCR = 0.0
FPAR = 0.0
TTVC = null
TOOL_CALLS_PER_VERIFIED_COMPLETION = null
TOKENS_PER_VERIFIED_COMPLETION = null
CONTEXT_TOKENS_PER_VERIFIED_COMPLETION = null
```

Failure-inclusive diagnostics such as TER, ESR, and RSR remain computable when
their own denominators are non-zero. No fast failed run receives a TTVC value.

## Fail-closed observation validation

The metric module rejects contradictory or malformed inputs, including:

- verified completion without TTVC;
- TTVC on a non-completing run;
- excluded/invalid run claiming verified completion;
- first-pass acceptance without verified completion;
- first-pass acceptance combined with a repair attempt;
- repair success without both a repair attempt and verified completion;
- surviving edit content on an unverified attempt;
- surviving edits exceeding proposed edits;
- tool errors exceeding tool calls;
- negative counts;
- non-finite or negative timing/overhead values;
- missing exclusion/invalid reason codes;
- negative Q4 artifact size.

## Metric authority boundary

A016 does not implement Repository Health Delta. That authority remains with
MSTR-000B B030:

```text
A016_REPOSITORY_HEALTH_DELTA = NOT_IMPLEMENTED
B030_REPOSITORY_HEALTH_DELTA_AUTHORITY = PRESERVED
```

A016 also does not create a verifier-health classifier, trajectory admission
authority, harness tournament result, or training signal.

## Candidate outputs

```text
src/mstr_qualify/metrics.py
tests/unit/test_metrics.py
evidence/mstr-000a/A016-metrics.md
```

`tasks.md` is intentionally unchanged in the implementation candidate. A016 may
be marked complete only after governed implementation merge, successful
post-merge proof, and a separate closeout.

## Authority containment

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_EXECUTION = NONE
SECRET_ACCESS = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B023_VERIFIER_HEALTH_EXECUTION = NOT_IMPLEMENTED_BY_A016
B030_REPOSITORY_HEALTH_DELTA = NOT_IMPLEMENTED_BY_A016
A017_STATE = PENDING
```
