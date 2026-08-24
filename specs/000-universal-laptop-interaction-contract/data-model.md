# MSTR-000 Data Model

The MSTR qualification harness uses versioned machine-readable records; Markdown reports summarize but do not replace evidence. SHA-256 is the default content/artifact hash. Unknown/missing mandatory identity fails material comparison.

## CandidateModel
Fields: `candidate_id`, upstream ID/revision, role, architecture family, total/active params, tokenizer identity, vision components, FIM status, runtime notes, status, rights decision. States: discovered -> static_qualified -> weight_eligible -> local_qualified -> finalist -> selected; or rejected/reference_only.

## RightsDecision
Fields: component kind/id/revision, license/terms URLs, tri-state personal/commercial/modification/fine-tuning/quantization/derivative redistribution, account/clickthrough/end-user-license requirements, field/scale restrictions, decision (`pass_permissive`, `pass_conditional`, `fail`, `reference_only`), rationale/reviewer/date.

## ModelArtifact
Fields: artifact ID, candidate/source revision, format, quant profile, quantizer/version/recipe, SHA-256, size, source, local-build flag, build manifest, timestamp. No run may reference an unpinned artifact.

## RuntimeBuild
Fields: runtime ID/project/version/commit/build flags/compiler/target OS+arch/acceleration/threads/binary hash/package size.

## HardwareProfile
Fields: tier, OS/build, CPU/arch/ISA/cores, RAM, acceleration presence/use, power mode, storage, editor/version/baseline memory, reference repo, context capability.

## DistributionContract
Versioned account/API/subscription/activation/acquisition gating/offline/network/telemetry/user-code/packaging/platform/update/uninstall behavior. Current logical ID `MSTR-DIST-v0`.

## InteractionContract
Fields: version, backbone/tokenizer identity constraints, prompt/chat template, stable prefix hash, FIM semantics, tool grammar, result serialization, edit grammar, stale-write semantics, context order, task-state schema, privacy/network semantics, runtime/cache assumptions, fixture revision.

## BenchmarkManifest
Fields: ID, purpose/surface, task list, candidates, seeds, sampling, timeout, verifier policy, tools/network, cache requirements, comparison policy, source commit.

## TaskManifest
Fields: task ID, repository/base revision, task text, workspace scope, required verifiers, timeout, seed/sampling, network/future-history policy, tool budget, hidden artifact references, benchmark exclusion, notes.

## RunEvidence
Fields: run/schema/protocol IDs, task/benchmark, candidate/artifact/runtime/hardware/interaction identities, context/cache, seed, latencies, disk/memory/paging, throughput, thermal/responsiveness, verifiers, final classification, logs. Immutable after finalization; corrections supersede rather than mutate.

## ContextArm
Components/versions, index settings, RAM/disk/start/update, token budget, localization/solve/TTVC refs, status experimental/default/rejected.

## EnvironmentTask
Repo/base/environment snapshot/dependency state/task/reference solution (hidden from solver)/oracle/no-op/unsolved/shortcuts/reset/provenance fields.

## VerifierDefinition
ID/type/command or deterministic implementation/fixtures/timeout/pass semantics/protected evaluator paths/anti-tamper/version/hash.

## ProvenanceRecord
Source/revision/time/license decision/hash/dedup lineage/benchmark exclusion/opt-out/transformations/parent provenance IDs.

## DecisionRecord
Subject, alternatives, evidence refs, decision, rationale, unresolved risks, authority/approver/effective commit/supersession.

## Relationships

```text
CandidateModel 1---N RightsDecision
CandidateModel 1---N ModelArtifact
RuntimeBuild/HardwareProfile/InteractionContract 1---N RunEvidence
BenchmarkManifest 1---N TaskManifest 1---N RunEvidence
ContextArm 1---N RunEvidence
EnvironmentTask 1---N VerifierDefinition
DecisionRecord N---N evidence/entities
ProvenanceRecord forms a lineage graph
```

## Required Persistence

```text
schemas/
artifacts/candidates/
artifacts/manifests/
artifacts/results/
artifacts/decisions/
```

Large logs, model files, caches, and environments are not committed. Repository records store hashes and locations.

## Validation Rules

- JSON validates against matching `schema_version`.
- IDs immutable; SHA-256 lowercase hex.
- Material run invalid without candidate/artifact/runtime/hardware/task identities.
- Direct report requires matching measurement protocol, task/verifier/timeout/cache/hardware class unless explicitly non-equivalent.
