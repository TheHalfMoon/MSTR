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

## Frozen by B028

```text
mstr.training-method-cell.v0
mstr.q4-promotion.v0
```

B028 freezes the equivalent-method tournament cell and fail-closed Q4 checkpoint-promotion contracts. Generic framework documentation is never candidate-specific arm support evidence: every concrete finalist/method cell must bind exact backbone/framework support evidence or an exact unsupported reason before execution. A later material checkpoint may parent another material weight-changing stage only when its `mstr.q4-promotion.v0` record is `PROMOTED`. B028 itself grants no training, model-weight access, paid compute, or model-execution authority.

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
mstr.material-result-identity.v0
mstr.research-experiment.v2
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
