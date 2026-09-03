# Contracts — MSTR-000B

MSTR-000B introduces design contracts that implementation tasks register into the runtime `schemas/` directory with tests and fixtures.

## Frozen by B001

```text
mstr.task-node.v0
mstr.task-eligibility.v0
```

B001 owns the byte-identical design/runtime schemas:

```text
specs/002-code-model-supremacy-foundation/contracts/mstr-task-node-v0.schema.json
schemas/mstr-task-node-v0.schema.json

specs/002-code-model-supremacy-foundation/contracts/mstr-task-eligibility-v0.schema.json
schemas/mstr-task-eligibility-v0.schema.json
```

`mstr.task-node.v0` freezes task state, prerequisites, outputs/evidence outputs, supersession, closeout rules, external-effect classes, exact-authority requirements, and candidate-pool prerequisites. `mstr.task-eligibility.v0` freezes the structured result consumed by B002 and later automation. It is fail-closed: `eligible=true` requires every represented prerequisite/authority/supersession/state/candidate-pool check to be satisfied and permits no top-level failure reason; `eligible=false` requires at least one reason.

For authority-gated external effects, `required_authority_id` is a foreign-key identity for an **already-canonical authority record/envelope**. The referenced authority—not the TaskNode—owns the exact authorized effect scope and any applicable cost/resource ceilings required by the constitution and canonical task. Task schema validation and B002 eligibility verification never create, widen, or replace that authority. Duplicating mutable scope/cost limits into TaskNode would create a second authority surface and is therefore intentionally avoided.


## Frozen by B026

```text
mstr.material-result-identity.v0
mstr.research-experiment.v2
```

B026 freezes exact material-result identity and a single-fidelity research-experiment record for the L0 -> L4 research ladder. Every material result carries exact model/artifact/tokenizer/quantizer/runtime/hardware/context/contracts/task/verifier/sampling/classification/cost identity where applicable and explicit `N/A` otherwise; training evidence additionally requires concrete data and checkpoint-relative difficulty identities. Ambiguous sentinels are invalid and a material artifact hash, when applicable, is an actual SHA-256. A promoted experiment binds one frozen evaluation identity, one fidelity level, complete material results, a predeclared budget, and the exact machine-readable hard-gate set for that fidelity level with every required gate passing. L1-L4 records require explicit immediate-predecessor `PROMOTE` evidence from the same campaign and frozen evaluation identity, and `parent_identity` must bind the predecessor's promoted result. Semantic validation enforces material-result count, declared wall-time/material-count/paid-cost ceilings, exact gate coverage, and external-effect authority references. Any external-effect resource class or cost must bind an immutable separately canonical authority record and remain within its declared scopes and ceilings; validation never creates or widens that authority. B026 also freezes `configs/research/mstr-research-ladder-v0.json`; it grants no campaign, model, weight, paid-compute, data-ingestion, training, RL, or release authority.

## Frozen by B028

```text
mstr.training-method-cell.v0
mstr.q4-promotion.v0
```

B028 freezes the equivalent-method tournament cell and fail-closed Q4 checkpoint-promotion contracts. Generic framework documentation is never candidate-specific arm support evidence: every concrete finalist/method cell must bind exact backbone/framework support evidence or an exact unsupported reason before execution. A later material checkpoint may parent another material weight-changing stage only when its `mstr.q4-promotion.v0` record is `PROMOTED`. B028 itself grants no training, model-weight access, paid compute, or model-execution authority.

## Frozen by B029

```text
mstr.adaptive-inference-policy.v0
mstr.selective-context-config.v0
```

B029 freezes one-attempt-by-default adaptive inference, verifier/uncertainty-gated targeted repair, bounded optional branching, positive expected-DVCR justification for extra compute, and explicit marginal accounting for extra tokens, seconds, and tool actions. The policy binds canonical A010 capability fields and B020 difficulty evidence without granting success or execution authority. Selective context freezes the seven canonical intent classes and maps them onto explicit H1-compatible retrieval primitives. Unsupported active-contract capabilities remain explicit and fail closed instead of being invented. B029 itself performs no model execution, weight access, paid compute, training, or production release.

Remaining planned contracts:

```text
mstr.backbone-candidate.v2
mstr.tokenizer-economics.v0
mstr.data-constitution.v0
mstr.software-evolution-record.v0
mstr.self-alignment-generation.v0
mstr.teacher-rescue-record.v0
mstr.difficulty-calibration.v0
mstr.verifier-health.v0
mstr.test-generation-example.v0
mstr.greenfield-task.v0
mstr.repository-health.v0
mstr.candidate-pool-decision.v0
```

## Cross-Contract Rules

1. Training admission consumes exact provenance, concrete rights decisions, contamination state, and verifier-health identity; missing/unresolved evidence fails closed.
2. Self-alignment binds provenance/rights to both the seed and every generated task/solution/test artifact before `ADMIT` is valid.
3. Teacher terms/identity are not sufficient rights proof; every concrete teacher output requires output provenance, rights decision, contamination status, independent execution, and verifier-health admission.
4. Generated-test examples require provenance, rights, contamination, protected-path integrity, and behavioral proof; `tests pass` alone is insufficient.
5. Difficulty records are invalid without exact student/model/harness/sampling identity.
6. Software-evolution projections must declare future-history visibility explicitly.
7. Candidate-pool decisions require comparable evidence or an explicit rejection/N/A reason. No-new-weight-access does not imply no-new-candidate qualification.
8. Every material research result uses `MaterialResultIdentity` with exact model/artifact/tokenizer/quantizer/runtime/hardware/context/contracts/task/verifier/sampling/classification/cost identity or an explicit not-applicable value; opaque result blobs cannot authorize comparison/promotion.
9. Research experiments bind to frozen evaluation identity and a single fidelity level.
10. Task eligibility never grants authority; it only verifies already-canonical authority/dependencies. Once B002 is canonical, B003+ execution/merge fails closed without exact-main `eligible=true`.
11. `Q4PromotionRecord` is required after every material weight-changing stage. Only a `PROMOTED` record with verified merged-master/Q4 hashes, pinned export/quantizer revisions and recipes, and passing required Q4/laptop regressions may parent a later material stage.
12. Q4 product evidence remains separate from master-checkpoint evidence.

Schema implementation belongs to the exact B-task named in `tasks.md`; an unimplemented planned contract has no runtime authority.

B026 research records resolve lineage and authority from repository-local immutable artifacts rather than trusting inline claims. Predecessors are SHA-256-bound experiment-registry records under `artifacts/results/research/<task>/registry/`; external authority is a SHA-256-bound foreign key to `artifacts/authorities/<authority_id>.json`. Governed effects are exhaustively declared, canonical scope/ceilings are derived from the resolved authority artifact, and L4 promotion requires concrete Q4/runtime/hardware identity plus exact Q4 evidence bindings.

### B026 content-addressed promotion policy and gate evidence

Research promotion is not self-attested. `promotion_policy_identity` and every hard-gate `evidence_identity` are lowercase `sha256:<digest>` content addresses resolved from the canonical registry templates frozen in `configs/research/mstr-research-ladder-v0.json`. A policy must bind the same governing task, campaign, fidelity level and frozen evaluator, must exactly cover the required gate IDs, and must predeclare `EQ`, `GTE`, `LTE`, or `NOT_APPLICABLE` criteria. Gate evidence binds task/campaign/experiment/gate and an observed value. The validator computes the gate status and rejects a submitted status that disagrees.

For L4, `q4_promotion_record_identity_or_na` is a content address into the Q4 promotion registry. The resolved existing `mstr.q4-promotion.v0` contract remains authoritative; B026 does not create Q4 execution, training, model, network, paid-compute, or release authority.


## B026 canonical history boundary

Campaign-result validation is Git-history-bound. Policy, predecessor, and external authority must already exist at an explicit canonical campaign-freeze commit. Gate/verifier/Q4 evidence must exist at a later canonical evidence commit. Both commits must be in `main` ancestry and the freeze commit must strictly precede the evidence commit. Working-tree presence is never sufficient.
