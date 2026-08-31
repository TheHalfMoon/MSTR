# A012 — Clean-Checkout Environment Reset / Setup Abstraction

**Task:** `MSTR-000A / A012`
**State:** `COMPLETE_CANONICAL`
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

> This terminal state is a closeout candidate until the dedicated closeout PR is itself qualified, independently reviewed, mandatory-premerge verified, guarded-merged, and post-closeout verified on canonical `main`.

## Canonical lifecycle evidence

```text
CANONICAL_IMPLEMENTATION_BASE = 3cb9f44569a7469e785ed8ffc4ea88080663adda
INITIAL_QUALIFICATION_RUN = 33401051608 / FAILURE / Markdown trailing whitespace; quality skipped
SUPERSEDED_QUALIFICATION_RUN = 33401175833 / SUCCESS / head 92439f3ceb40be725eb1d126c79998ff26882816
SUPERSEDED_QUALIFICATION_RUN_2 = 33401772264 / SUCCESS / head 9bb9669d5c76f2fe78aebd5e9751b41f742648dc
FINAL_IMPLEMENTATION_HEAD = b75397999f8b84ab5abbfe0ef1614af99705864c
FINAL_IMPLEMENTATION_TREE = 9c032ec0fd1f531d90c9de1603779095d4250302
FINAL_EXACT_HEAD_QUALIFICATION = 33410772058 / SUCCESS / 15 focused / 988 full / schema 23 valid + 23 invalid / Ruff PASS / mypy PASS
EXACT_HEAD_REVIEW = 5068484080 / COMMENTED / NO_BLOCKING_FINDING
UNRESOLVED_REVIEW_THREADS = 0
MANDATORY_PREMERGE = 33411107991 / SUCCESS
IMPLEMENTATION_PR = 109
IMPLEMENTATION_MERGE = 95a9014de72bd31e6763a2323c31a25a42974302
IMPLEMENTATION_MERGE_TREE = 9c032ec0fd1f531d90c9de1603779095d4250302
POST_MERGE_VERIFICATION_RUN = 33411593331 / SUCCESS
A012_STATE = COMPLETE_CANONICAL_CANDIDATE
A013_STATE = PENDING
```

The failed and superseded workflow runs above remain preserved as negative or head-specific evidence and are not represented as final qualification. A012 grants no environment admission, network, secret, model, paid-compute, training, private-data, large-dataset, or production-release authority. A006 remains the protected final success authority. A013 remains independently gated and is not made complete by this closeout.
