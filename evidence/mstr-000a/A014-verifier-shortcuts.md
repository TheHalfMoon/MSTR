# A014 — Verifier Runner + Reward-Shortcut Battery

**Task:** `MSTR-000A / A014`
**State:** `COMPLETE_CANONICAL`
**Canonical base:** `d1d0587aac1bbe1daf32f899810a20a519c31f5d`

## Entry decision

A013 is `COMPLETE_CANONICAL` on the canonical base. A006 remains the protected terminal-success authority. No open PR owns the A014 verifier surface; the live open MSTR-000 PRs are separate T029/T030 work. A014 is an early-safe, model-independent task and is manually exact-prerequisite governed; the MSTR-000B machine task gate covers B-tasks, not A014.

A014 is also an explicit prerequisite of MSTR-000B B023 verifier-health implementation. This implementation therefore produces verifier evidence and reward-shortcut resistance only; it does not implement B023 health classification and does not create a parallel terminal-success authority.

## Canonical implementation scope

```text
src/mstr_qualify/verifier/runner.py
tests/integration/test_verifier_runner.py
tests/security/test_verifier_shortcuts.py
src/mstr_qualify/verifier/__init__.py
evidence/mstr-000a/A014-verifier-shortcuts.md
```

The implementation was merged through PR #114 and re-proven on canonical `main` before this dedicated closeout marks A014 complete in `tasks.md`.

## Verifier runner semantics

The controlled A014 runner:

- validates the canonical `mstr.verifier-manifest.v0` contract;
- requires `finalizer_contract_id=A006_PROTECTED_FINALIZER`;
- requires `success_semantics=VERIFIER_EVIDENCE_ONLY`;
- derives verifier `PASS`/`FAIL` from expected process exit codes, never from model/verifier stdout claims;
- emits deterministic result identities binding verifier id, source identity, exit code, status, and stdout/stderr hashes;
- requires every verifier source identity to live inside a protected path;
- hashes verifier source identity before and after execution;
- snapshots protected paths before and after execution;
- rejects protected-path writes/tamper;
- requires complete read/write/network effect observation from the injected controlled executor;
- rejects observed prohibited network activity;
- rejects reads from explicitly prohibited cached/future-solution prefixes;
- rejects network/secret/external-authority manifests for the A014 controlled-fixture lane;
- requires at least one required verifier;
- does not emit `run.completed`, `VERIFIED_SUCCESS`, or any substitute terminal-success event.

## Reward-shortcut battery

The battery fails closed unless all canonical A014 shortcut classes are represented:

```text
TEST_EVALUATOR_DELETION
ASSERTION_WEAKENING
HARDCODING
OUTPUT_SPOOFING
CACHED_SOLUTION_LEAKAGE
FUTURE_SOLUTION_LEAKAGE
PROHIBITED_NETWORK
PROTECTED_PATH_TAMPER
```

It also consumes the A011 manifest fixture contract and requires:

```text
known_good -> PASS
known_bad  -> REJECT/FAIL
noop       -> REJECT/FAIL
```

Every declared shortcut class is bound to an allowlisted detection mechanism. A shortcut case cannot be marked expected-pass, and a rejection caused by an unrelated error does not satisfy the declared shortcut class. Cached/future leakage requires an observed `verifier.solution_leakage` signal; prohibited network requires `verifier.prohibited_network`; evaluator/protected-path attacks require matching integrity/tamper evidence; hardcoding and output-spoof fixtures require an actual verifier failure rather than claimed stdout success.

Controlled security fixtures exercise evaluator deletion, in-execution assertion weakening, protected-path mutation, failing-exit stdout spoofing, cached/future read observation, network observation, and hardcoded/no-op failure behavior. A missing shortcut class, mismatched detection mechanism, or shortcut fixture declared as expected-pass is a hard failure.

## Security and authority containment

```text
TERMINAL_SUCCESS_AUTHORITY = A006_PROTECTED_FINALIZER
A014_OUTPUT = VERIFIER_EVIDENCE_ONLY
B023_VERIFIER_HEALTH_CLASSIFICATION = NOT_IMPLEMENTED_BY_A014
REAL_ENVIRONMENT_EXECUTION = NOT_AUTHORIZED
NETWORK_EXECUTION = NONE
SECRET_ACCESS = NONE
EXTERNAL_AUTHORITY_ID = NONE
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
```

The injected executor abstraction is intentionally not a generic unisolated subprocess implementation. A014 requires complete effect observations from a controlled fixture or separately admitted isolation layer; absence of such evidence fails closed.

## Canonical lifecycle evidence

```text
CANONICAL_IMPLEMENTATION_BASE = d1d0587aac1bbe1daf32f899810a20a519c31f5d
FINAL_IMPLEMENTATION_HEAD = 3c61c9f792027d36c20cdf5ad921eca29ce3f6de
FINAL_IMPLEMENTATION_TREE = 8e3c960f5452842cb359d4b9a9ed1c1c34cdc45f
FINAL_EXACT_HEAD_QUALIFICATION = 33422233350 / SUCCESS
EXACT_HEAD_REVIEW = 5069578156 / COMMENTED / NO_BLOCKING_FINDING
UNRESOLVED_REVIEW_THREADS = 0
MANDATORY_PREMERGE = 33422524606 / SUCCESS
IMPLEMENTATION_PR = 114
IMPLEMENTATION_MERGE = 87f1636e434ec36f508528ab4a78204adf103856
IMPLEMENTATION_MERGE_TREE = 8e3c960f5452842cb359d4b9a9ed1c1c34cdc45f
POST_MERGE_VERIFICATION_RUN = 33422854862 / SUCCESS
INITIAL_CLOSEOUT_QUALIFICATION = 33423959583 / FAILURE / IDENTITY_SCOPE / TRAILING_WHITESPACE
A014_STATE = COMPLETE_CANONICAL_CANDIDATE
A015_STATE = PENDING
```

Negative qualification evidence remains preserved and is not reused as PASS:

```text
33421271341 = FAILURE / identity_scope / trailing whitespace found by git diff --check
33421460726 = FAILURE / quality / Ruff import ordering after focused tests, schema validation, and 1007 full pytest passed
33421732025 = FAILURE / quality / one mypy typing error after focused tests, schema validation, full pytest, and Ruff passed
33423959583 = FAILURE / closeout identity_scope / trailing whitespace found by git diff --check before quality
```

The initial closeout qualification failed before quality because `git diff --check` found trailing whitespace on two newly changed A014 lines in `tasks.md`. That run remains preserved as negative evidence and is not represented as passing.

An independent pre-PR security review also found that shortcut labels could be satisfied by unrelated failures. The final implementation head fixed that issue by binding each shortcut class to compatible detection codes and adding negative mismatch/expected-pass tests. The final exact-head qualification then proved:

```text
focused_A014 = 9 passed
schema_validation = PASS / 23 valid fixtures + 23 invalid fixtures
full_pytest = 1009 passed
ruff = PASS
mypy = PASS / 39 source files
```

The implementation head was qualified before PR creation, independently reviewed on that immutable head, mandatory-premerge verified, guarded-merged with the expected head SHA, and then re-proven on canonical `main` by post-merge run `33422854862` with identity, quality, and final canonical-ref recheck all successful.

> This terminal state is a closeout candidate until the dedicated closeout PR is itself qualified, independently reviewed, mandatory-premerge verified, guarded-merged, and post-closeout verified on canonical `main`.

This closeout does not widen A014 beyond controlled verifier evidence. A006 remains the only protected terminal-success authority. B023 verifier-health classification remains independently gated, A015 remains pending, and no real-environment, network, secret, model, model-weight, paid-compute, large-dataset, weight-changing-training, large-scale-RL, or production-release authority is granted.
