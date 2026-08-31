# A012 — Clean-Checkout Environment Reset / Setup Abstraction

**Task:** `MSTR-000A / A012`
**State:** `IMPLEMENTATION_CANDIDATE`
**Canonical base:** `3cb9f44569a7469e785ed8ffc4ea88080663adda`

## Implemented boundary

A012 implements the smallest repository-local reset/setup layer that consumes the A011 `mstr.environment-manifest.v0` and `mstr.setup-manifest.v0` contracts without creating environment-admission or terminal-success authority.

The implementation:

- validates both frozen A011 schemas before execution;
- cross-binds environment ID, setup ID, health targets, effect policy, and resource ceilings;
- fails closed unless reset/setup worktree writes are explicitly `WORKTREE_AND_TEMP`;
- supports exact local `HARD_RESET_CLEAN` using only local Git reset/clean operations;
- proves the expected repository origin before any destructive `reset --hard` or `clean` operation, then re-proves origin, revision, tree, and clean state after reset;
- requires `FRESH_CLONE` to be supplied by an injected driver and never opens network implicitly;
- requires any injected fresh-clone driver to attest the same exact effect/resource envelope as the manifests;
- executes setup only through an injected executor whose declared enforcement envelope exactly equals the manifest effect/resource envelope;
- rejects all network-bearing or secret-bearing manifests in A012 itself; later tasks must introduce any separately authorized external-effect execution path;
- contains setup working directories to the reset workspace;
- snapshots protected paths by content/type/mode fingerprint after reset and rejects any setup mutation, including Git-ignored protected paths that `git status` would not report;
- fails closed on setup timeout/failure and protected-path mutation;
- records setup steps, repository identity, health/checker identities, effects, and resource limits;
- returns `admission_status=NOT_EVALUATED_A013`; A013 remains the independent health-target/bootstrap admission authority.

## Authority boundary

```text
A012_CANONICAL_EXECUTION_PROFILE = LOCAL_RESET_AND_REPOSITORY_FIXTURES_ONLY
NETWORK_EXECUTION = NONE
SECRET_ACCESS = NONE
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PRODUCTION_RELEASE = NONE
ENVIRONMENT_ADMISSION_AUTHORITY = A013 / NOT_CREATED_BY_A012
TERMINAL_SUCCESS_AUTHORITY = A006_PROTECTED_FINALIZER
```

A manifest carrying network or secret effects is rejected by this A012 implementation even if it names an authority ID. A future canonical task may add a separately authorized execution path, but generic continuation or an arbitrary authority string does not widen A012.

## Qualification and hardening history

- `33401051608` = `FAILURE` at `git diff --check` because the initial candidate evidence contained Markdown trailing whitespace. Quality jobs were skipped. The failure is preserved as negative evidence and is not represented as passing.
- `33401175833` = `SUCCESS` on superseded exact head `92439f3ceb40be725eb1d126c79998ff26882816`: focused A012 tests `8 passed`; schema validation passed; full pytest `981 passed`; Ruff passed; mypy passed with no issues in 37 source files; immutable identity recheck passed.
- Pre-review patch inspection identified destructive-scope hardening: local `HARD_RESET_CLEAN` verified repository origin only after destructive reset/clean. The candidate was amended so expected origin is proven before any destructive Git command and re-proven afterward. A dedicated security regression proves a wrong-origin workspace reaches no reset/clean command.
- `33401772264` = `SUCCESS` on superseded exact head `9bb9669d5c76f2fe78aebd5e9751b41f742648dc`: focused A012 tests `9 passed`; schema validation passed; full pytest `982 passed`; Ruff passed; mypy passed with no issues in 37 source files; immutable identity recheck passed.
- Further review found that A011 permits `filesystem_writes = NONE | TEMP_ONLY | WORKTREE_AND_TEMP`; because reset writes the checkout, A012 now rejects narrower write policies before mutation.
- The execution boundary was then made explicitly local-only: network/secret manifests are rejected rather than trusting a caller-supplied authority string; a fresh-clone driver must attest the exact manifest envelope.
- Protected-path verification was strengthened from Git-status visibility to deterministic content/type/mode fingerprinting so ignored/untracked protected paths cannot be modified silently.

Every successful historical qualification remains valid evidence only for its immutable superseded head. The final hardened head requires a fresh complete exact-head qualification before review/merge admission.

## Required qualification

This candidate is not canonical until current exact-head hosted qualification, independent review, mandatory premerge verification, guarded expected-head merge, post-merge proof, canonical closeout, and post-closeout proof succeed. Failed or superseded runs remain evidence and must not be rewritten as passing.
