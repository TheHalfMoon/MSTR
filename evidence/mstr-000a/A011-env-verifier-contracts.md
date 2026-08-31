# A011 — Environment / Setup / Verifier Contract Freeze

**Task:** `MSTR-000A / A011`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical base:** `17985cb7176bb99df6139c1d3fbc23c6de4e3bf0`

## Contract boundary

A011 freezes three repository-local Draft 2020-12 contracts: `mstr.environment-manifest.v0`, `mstr.setup-manifest.v0`, and `mstr.verifier-manifest.v0`. They bind exact repository revision/tree identity, clean-reset requirements, bounded setup attempts, health-target and independent-checker identities, verifier source identity, protected paths, resource ceilings, and explicit effect policy.

The effect policy is fail-closed: `network_access=NONE` requires an empty host allowlist; network allowlisting requires an explicit authority identity; secret access is independently declared and likewise requires exact secret identifiers plus authority. No contract field itself grants external-effect authority.

Verifier manifests are evidence producers only. `finalizer_contract_id` is frozen to `A006_PROTECTED_FINALIZER`, and `success_semantics` is frozen to `VERIFIER_EVIDENCE_ONLY`; therefore A011 cannot create a second success authority. B022 verifier-health remains the health-record authority and is not duplicated here.

Known-good, known-bad, and no-op fixture identities are part of the verifier contract. Repository-owned synthetic fixtures validate contract behavior only; A011 does not execute setup, network calls, secrets, models, external verifiers, or production workloads.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_EXECUTION = NONE
SECRET_ACCESS = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PRODUCTION_RELEASE = NONE
A011_AUTHORITY = CONTRACT_SCHEMA_AND_REPOSITORY_FIXTURES_ONLY
```

A011 remains non-canonical until exact-head qualification, review, mandatory premerge verification, guarded merge, post-merge proof, canonical closeout, and post-closeout proof succeed.
