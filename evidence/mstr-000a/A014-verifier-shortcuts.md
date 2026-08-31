# A014 — Verifier Runner + Reward-Shortcut Battery

**Task:** `MSTR-000A / A014`
**State:** `IMPLEMENTATION_CANDIDATE`
**Canonical base:** `d1d0587aac1bbe1daf32f899810a20a519c31f5d`

## Entry decision

A013 is `COMPLETE_CANONICAL` on the canonical base. A006 remains the protected terminal-success authority. No open PR owns the A014 verifier surface; the live open MSTR-000 PRs are separate T029/T030 work. A014 is an early-safe, model-independent task and is manually exact-prerequisite governed; the MSTR-000B machine task gate covers B-tasks, not A014.

A014 is also an explicit prerequisite of MSTR-000B B023 verifier-health implementation. This implementation therefore produces verifier evidence and reward-shortcut resistance only; it does not implement B023 health classification and does not create a parallel terminal-success authority.

## Candidate scope

```text
src/mstr_qualify/verifier/runner.py
tests/integration/test_verifier_runner.py
tests/security/test_verifier_shortcuts.py
src/mstr_qualify/verifier/__init__.py
evidence/mstr-000a/A014-verifier-shortcuts.md
```

`specs/001-agent-harness-verified-loop-foundation/tasks.md` intentionally remains unchanged until implementation evidence is proven and canonical closeout is authorized by the completed lifecycle.

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

Controlled security fixtures exercise evaluator deletion, in-execution assertion weakening, protected-path mutation, failing-exit stdout spoofing, cached/future read observation, network observation, and hardcoded/no-op failure behavior. A missing shortcut class is itself a hard failure.

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

## Required qualification

This candidate is not canonical until a fresh exact-head hosted qualification proves:

1. focused A014 integration/security tests;
2. repository schema validation;
3. full pytest;
4. Ruff;
5. strict mypy;
6. exact head/tree/scope identity and immutable recheck.

After qualification, the exact patch requires independent review, mandatory exact-head premerge qualification, guarded expected-head merge, post-merge proof, and a separate canonical closeout before A014 may be marked complete in `tasks.md`.

Historical or stale test results are not reusable as PASS for this candidate.
