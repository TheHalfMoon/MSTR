# MSTR Storage Architecture — Zero-Large-Artifact Founder Environment

**Status:** CANONICAL_STORAGE_POLICY (founder decision 2026-08-26)
**Supersedes:** any prior expectation that acquired model binaries persist on the founder's local development machine (including the local-persistence clause of the T027 `retention_policy`).
**Preserves:** every candidate identity, immutable revision, per-file SHA-256/LFS OID, byte size, rights decision, network allowlist, gating status, and the USD 0.00 acquisition ceiling recorded in `artifacts/manifests/T027-weight-access.json` (SHA-256 `68f514ab8d1cea11c82f49c260dd7c9b9e1348a2cbbb561bbbb45439b3455e1e`). Nothing about *what* is acquired changes; only *where* and *for how long* binaries live.

## Invariant

```text
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
MAC_RECEIVES = SOURCE_CODE | CONFIGS | MANIFESTS | HASHES | METRICS | EVIDENCE | REPORTS
MODEL_BINARIES_ON_MAC = PROHIBITED
GIT_TREE_BINARIES      = PROHIBITED (unchanged; .gitignore enforcement stands)
```

No safetensors, GGUF, ONNX, checkpoint, quantization output, dataset blob, or other large model artifact may be stored on the founder Mac or committed to Git.

## Execution model

```text
ACQUISITION_ENVIRONMENT       = CLOUD_EPHEMERAL_RUNNERS
COLAB                         = designated interactive/primary environment (founder-driven)
ACTIONS_EPHEMERAL_RUNNER      = approved autonomous executor (public-repo runners, USD 0.00)
RUNNER_LIFETIME               = single job; local copies destroyed with the VM after evidence is finalized
PERSISTENCE_FOR_ORIGINALS     = upstream Hugging Face at immutable pinned revisions (authoritative, reproducible)
PERSISTENCE_FOR_DERIVED       = none by default; derived artifacts (Q4/GGUF etc.) are regenerated on demand inside ephemeral runners, with their identity (tool commit + recipe + output SHA-256) recorded in Git manifests
COST_CEILING                  = USD 0.00 (unchanged)
```

## Ephemeral runner contract (binding)

Every acquisition/conversion/evaluation-preparation run MUST:

1. read authority only from the canonical T027 manifest (exact candidates, revisions, filenames);
2. fetch via HTTPS GET restricted to the manifest's declared host allowlist;
3. verify every downloaded byte stream against the frozen per-file SHA-256/LFS OID and byte size — mismatch is a hard candidate failure;
4. never authenticate, never accept gated terms, never spend money;
5. emit a machine-verifiable acquisition report (per-file status + hashes + sizes) as its durable output;
6. retain local binary copies no longer than the duration of the run; destruction with the ephemeral VM satisfies deletion;
7. produce no artifact that outlives the run except reports/manifests/evidence, which return to Git.

## Consequences for downstream tasks

- **T028** executes through an approved ephemeral runner; the durable outputs are the per-candidate reports, the verified aggregate manifest, and evidence.
- **T029–T033** (quantization, runtime qualification, memory/sustained/regression measurement) execute inside ephemeral runners that re-acquire pinned inputs per run; measured metrics/hashes return to Git. Where a task's canonical wording says "local," it is interpreted as "on the qualified reference runner lane," not on the founder Mac.
- **T034 admission** judges candidates from returned evidence, not from binaries resident anywhere persistent.
- Any task needing long-lived derived binaries must first obtain a separate founder decision on cloud-side persistent storage; until then, regenerate-on-demand is the default.

## Machine-readable amendment

`artifacts/manifests/T028-storage-amendment.json` encodes this decision and binds it to the exact T027 manifest by path, id, and SHA-256. The T027 manifest itself is intentionally left byte-for-byte untouched.
