# T028 — Weight Acquisition Evidence (Zero-Large-Artifact Architecture)

**Task:** MSTR-000 / T028
**Authority:** founder T028 authorization against frozen manifest `mstr.weight-access-manifest.v1` / `T027-weight-access-preflight-frozen` (`artifacts/manifests/T027-weight-access.json`, SHA-256 `68f514ab8d1cea11c82f49c260dd7c9b9e1348a2cbbb561bbbb45439b3455e1e`), plus the zero-large-artifact storage amendment (`docs/canonical/STORAGE_ARCHITECTURE.md`, `artifacts/manifests/T028-storage-amendment.json`).

## Result

```text
ALL EIGHT CANDIDATES = ACQUIRED_VERIFIED
COST = USD 0.00
AUTHENTICATION = none used
GATED_TERMS = none accepted
BINARIES_ON_FOUNDER_MAC = ZERO (ephemeral runner VMs only; deleted after verification)
BINARIES_IN_GIT = ZERO (reports/manifests only)
```

## Execution

Each candidate was acquired in a dedicated ephemeral GitHub Actions public-repo runner job (USD 0.00, unauthenticated, HTTPS GET to huggingface.co only per the T027 allowlist). The runner streamed each pinned file, verified size + SHA-256 per file against the frozen manifest, emitted a machine-verifiable report as its durable output, and deleted local binary copies before exit. VM reclamation enforces final deletion.

Run IDs (all `workflow_dispatch` on canonical main):

| candidate | Actions run |
|---|---|
| qwen3.5-2b | 32940533048 |
| qwen3.5-4b | 32940968955 |
| ministral-3-3b | 32940976594 |
| qwen3-4b | 32940984016 |
| granite-4.1-3b | 32940990851 |
| smollm3-3b | 32940997382 |
| qwen2.5-coder-1.5b | 32941004536 |
| yi-coder-1.5b | 32941011661 |

## Verification

All 8 per-candidate reports were cross-checked locally via `verify_acquisition_report()` against the frozen manifest: every declared file present, every hash and byte size exact, no unknown files, no substitutions, no `latest` refs. Aggregate verdict:

```text
granite-4.1-3b         ACQUIRED_VERIFIED
ministral-3-3b         ACQUIRED_VERIFIED
qwen2.5-coder-1.5b     ACQUIRED_VERIFIED
qwen3-4b               ACQUIRED_VERIFIED
qwen3.5-2b             ACQUIRED_VERIFIED
qwen3.5-4b             ACQUIRED_VERIFIED
smollm3-3b             ACQUIRED_VERIFIED
yi-coder-1.5b          ACQUIRED_VERIFIED
```

T024-compatible per-candidate artifact manifests were emitted from verified reports:
`artifacts/manifests/T028-artifact-<candidate_id>.json`.

## Boundary

This proves acquisition and integrity only. It does NOT prove LOCAL_QUALIFIED, FINALIST, BACKBONE_SELECTED, or any quality claim. No weights were transformed during T028. No binaries persist anywhere after evidence capture.
