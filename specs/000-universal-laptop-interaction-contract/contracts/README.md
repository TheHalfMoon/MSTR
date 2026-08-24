# MSTR-000 Contracts

Machine-readable boundaries for the qualification harness.

- `candidate-record.schema.json` — static candidate + rights record.
- `task-manifest.schema.json` — frozen task execution contract.
- `run-evidence.schema.json` — measured run evidence.
- `interaction-contract.schema.json` — prompt/tool/edit/cache contract identity.

Rules: JSON Schema validation required; schemas versioned; Markdown does not replace evidence; unknown core fields disallowed unless schema permits; binaries referenced by hashes/locations; secrets/tokens/private code/hidden-test content never stored in evidence records.

Runtime copies live under `schemas/`; records live under `artifacts/{candidates,manifests,results,decisions}/`.
