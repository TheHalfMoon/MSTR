# A013 — Bounded Environment Bootstrap / Admission Loop

**Task:** `MSTR-000A / A013`
**State:** `COMPLETE_CANONICAL`
**Canonical base:** `f82eb0c4c78080792ff9ca84f07690e4a972a3f8`

## Entry decision

A013 is an early-safe, model-independent task. Manual exact-prerequisite verification on the canonical base established:

```text
A012 = COMPLETE_CANONICAL
A012_POST_CLOSEOUT_PROOF = 33413683309 / SUCCESS
A_TASK_MACHINE_GATE_SCOPE_RECONCILIATION = PR #111 / merge f82eb0c4c78080792ff9ca84f07690e4a972a3f8
ACTIVE_CONFLICTING_ENVIRONMENT_ADMISSION_PR = NONE
UNQUALIFIED_CANDIDATE_RESULT_CONSUMED = NONE
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_EFFECT_AUTHORITY = NONE
SECRET_ACCESS = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PRODUCTION_RELEASE = NONE
```

The canonical B002 machine task gate covers MSTR-000B `B001-B034`; A001-A018 remain under manual exact-prerequisite verification unless a later canonical A-task catalog explicitly extends that coverage.

## Implemented boundary

A013 adds a bounded admission layer over A012 rather than duplicating reset/setup behavior.

The implementation:

- validates and cross-binds the frozen A011 environment/setup manifests before admission attempts;
- consumes `max_attempts`, declared health-target identities, checker identities, repository revision/tree identity, verifier-manifest identity, effect policy, and resource limits from those contracts;
- rejects network-bearing, secret-bearing, or external-authority-bearing manifests at the A013 fixture boundary before setup execution;
- requires the injected independent checker registry to match every declared checker identity and cover every declared health target;
- requires independent checkers to attest network-isolated, secret-free, worktree-read-only effects;
- delegates every setup attempt to A012 `prepare_environment`, preserving exact clean-checkout reset, setup-envelope, protected-path, and repository-identity enforcement;
- verifies that A012 still returns `admission_status=NOT_EVALUATED_A013`, preventing delegated setup from self-declaring admission;
- runs every declared independent checker after a successful setup attempt and validates returned checker/target identity;
- records typed checker failures and setup failures as attempt evidence;
- admits only when all declared health targets pass within the same attempt;
- retries after setup or health-check failure from a fresh A012 reset up to the setup manifest attempt ceiling;
- returns `REJECTED` when the attempt ceiling is exhausted rather than manufacturing readiness.

Controlled fixture coverage proves first-attempt success, failed-check recovery, setup-failure recovery, exact retry ceilings, clean-reset reproducibility between attempts, all-target conjunction, typed checker-failure evidence, checker-identity/target fail-closed behavior, checker effect isolation, manifest binding rejection, and inherited no-network admission behavior.

## Authority boundary

A013 creates only the logical admission result for repository-controlled local fixtures used to test the bounded loop contract. It does **not** authorize a real training, benchmark, research, or production environment.

```text
A013_CANONICAL_EXECUTION_PROFILE = LOCAL_CONTROLLED_FIXTURES_ONLY
REAL_ENVIRONMENT_ADMISSION = PROHIBITED_PENDING_A014_AND_REMAINING_ENVIRONMENT_GATES
A014_VERIFIER_RUNNER = NOT_IMPLEMENTED_BY_A013
REWARD_SHORTCUT_BATTERY = NOT_IMPLEMENTED_BY_A013
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
TERMINAL_SUCCESS_AUTHORITY = A006_PROTECTED_FINALIZER
```

The implementation-readiness checklist still requires the reward-shortcut battery and the remaining environment-execution gates before any real environment execution/admission. A014 remains independently gated and is not made complete by A013.

> This terminal state is a closeout candidate until the dedicated closeout PR is itself qualified, independently reviewed, mandatory-premerge verified, guarded-merged, and post-closeout verified on canonical `main`.

## Canonical lifecycle evidence

```text
CANONICAL_IMPLEMENTATION_BASE = f82eb0c4c78080792ff9ca84f07690e4a972a3f8
FINAL_IMPLEMENTATION_HEAD = a4c67bc06e7174e58ee71a6a36727cea7658e8d8
FINAL_IMPLEMENTATION_TREE = e2abf8332c6149b0d3fac5ed82e7a494f5068783
FINAL_EXACT_HEAD_QUALIFICATION = 33415696480 / SUCCESS
EXACT_HEAD_REVIEW = 5069078478 / COMMENTED / NO_BLOCKING_FINDING
UNRESOLVED_REVIEW_THREADS = 0
MANDATORY_PREMERGE = 33417468208 / SUCCESS
IMPLEMENTATION_PR = 112
IMPLEMENTATION_MERGE = 1f22a4d91c1874cd18454e63cc87d92e18f9e14a
IMPLEMENTATION_MERGE_TREE = e2abf8332c6149b0d3fac5ed82e7a494f5068783
POST_MERGE_VERIFICATION_RUN = 33417713420 / SUCCESS
INITIAL_CLOSEOUT_QUALIFICATION = 33418142861 / FAILURE / IDENTITY_SCOPE_BEFORE_QUALITY / SUPERSEDED_AFTER_CHECKLIST_FORMATTING_REPAIR
A013_STATE = COMPLETE_CANONICAL_CANDIDATE
A014_STATE = PENDING
```

The failed initial closeout qualification remains preserved as negative evidence and is not represented as passing. The exact implementation head was qualified before PR creation, independently reviewed on that immutable head, mandatory-premerge verified, guarded-merged with the expected head SHA, and then re-proven on canonical `main`. This closeout does not widen A013 beyond the repository-controlled local-fixture boundary and grants no A014, real-environment, network, secret, model, model-weight, paid-compute, large-dataset, weight-changing-training, or production-release authority. A006 remains the protected terminal-success authority, and A014 remains independently gated.
