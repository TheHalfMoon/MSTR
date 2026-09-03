# B029 — Adaptive Test-Time Compute and Selective Context Policy

**Task:** `MSTR-000B / B029`
**State:** `IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT`
**Canonical entry main:** `1179515986ee2311ec1cd675fd899a6143c03761`

## Entry gate

```text
ENTRY_GATE_V1 = 33791919427 / FAILURE / EVIDENCE_HARNESS_ASSERTION_ONLY
ENTRY_GATE_V1_PRODUCTION_ELIGIBILITY = eligible=true / reasons=[]
ENTRY_GATE_V2 = 33792125789 / SUCCESS
CANONICAL_MAIN = 1179515986ee2311ec1cd675fd899a6143c03761
DRIFT = CLEAN
B029_ELIGIBLE = true
AUTHORITY_REQUIRED = false
CANDIDATE_POOL_REQUIREMENT = false
```

The first evidence workflow incorrectly asserted a legacy top-level `authority_required` field. The production `mstr.task-eligibility.v0` payload itself already reported `eligible=true`; v2 asserted the canonical nested `authority_result.required=false` and `candidate_pool_result.required=false` fields and completed successfully. The failed run remains negative evidence and is not represented as a pass.

## Builder evidence

```text
BUILDER_V1 = 33794038421 / FAILURE / RUFF_E501_AFTER_FULL_TEST_PASS
BUILDER_V2 = 33794732024 / FAILURE / FINAL_DIFF_CHECK_TRAILING_WHITESPACE
BUILDER_V3 = 33795227237 / SUCCESS
BUILDER_V1_FULL_PYTEST = 1285 passed
BUILDER_V2_FULL_PYTEST = 1285 passed
```

## Frozen contracts

B029 registers byte-identical design/runtime schemas and valid/invalid fixtures for:

```text
mstr.adaptive-inference-policy.v0
mstr.selective-context-config.v0
```

### Adaptive inference

```text
DEFAULT_ATTEMPTS = 1
ESCALATION_TRIGGERS = VERIFIER_FAILURE | UNCERTAINTY
NEW_EVIDENCE_REQUIRED_BEFORE_RETRY = true
TARGETED_REPAIR = enabled
OPTIONAL_BRANCHING = bounded-or-disabled
EXTRA_COMPUTE_RULE = POSITIVE_EXPECTED_DVCR_GAIN_REQUIRED
MARGINAL_ACCOUNTING = extra_tokens + extra_seconds + extra_tool_actions
PROTECTED_FINALIZER_REQUIRED = true
BUILDER_SUCCESS_AUTHORITY = false
```

The contract consumes, rather than duplicates, canonical dependencies: A005 provides bounded loop/repair/tool semantics; A006 preserves protected verifier/finalizer authority; A010 supplies `reliable_context_budget`, `recommended_verifier_cadence`, and `max_repair_depth`; B020 supplies checkpoint-relative difficulty evidence for nontrivial escalation. Numeric fixture caps are synthetic test values only and are not real-model capability claims.

### Selective context

The config contract freezes the seven canonical intent classes:

```text
NO_RETRIEVAL
NEED_FILE
NEED_SYMBOL
NEED_HISTORY
NEED_TEST
NEED_CONFIG
NO_MORE_CONTEXT
```

H1 compatibility is fail-closed. `NO_RETRIEVAL` and `NO_MORE_CONTEXT` consume no repository call; file/test/config intents resolve through explicit paths; symbol intent may search and then select explicit paths. The current H1 contract does not expose a history-retrieval endpoint, so the canonical fixture records `NEED_HISTORY = UNSUPPORTED_BY_ACTIVE_CONTRACT` rather than fabricating support. A later active interaction contract may supply that capability under its own authority and evidence. Implicit retrieval remains prohibited.

Context limits bind the A010 `reliable_context_budget` capability field and preserve compact AgentState, deterministic explicit paths, and deduplication. The policy does not claim retrieval ranking, prefix-cache performance, or model capability from configuration alone.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B029_AUTHORITY = CONTRACT_POLICY_ONLY
```

B029 freezes policy and local validation only. It does not run a model, spend paid compute, authorize extra inference, or change B011/B013 authority. Any later execution remains independently governed.
