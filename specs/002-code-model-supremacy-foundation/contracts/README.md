# Contracts — MSTR-000B

MSTR-000B introduces design contracts that implementation tasks will register into the runtime `schemas/` directory with tests and fixtures.

Planned contracts:

```text
mstr.task-node.v0
mstr.task-eligibility.v0
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
mstr.research-experiment.v2
mstr.training-method-cell.v0
mstr.repository-health.v0
mstr.candidate-pool-decision.v0
```

## Cross-Contract Rules

1. Training admission consumes exact provenance, contamination and verifier-health state.
2. Difficulty records are invalid without exact student/model/harness/sampling identity.
3. Teacher records never bypass verifier-health or rights requirements.
4. Software-evolution projections must declare future-history visibility explicitly.
5. Candidate-pool decisions require comparable evidence or an explicit rejection/N/A reason.
6. Research experiments bind to frozen evaluation identity and a single fidelity level.
7. Task eligibility never grants authority; it only verifies already-canonical authority/dependencies.
8. Q4 product evidence remains separate from master-checkpoint evidence.

Schema implementation belongs to the exact B-task named in `tasks.md`; this planning package does not register incomplete runtime schemas prematurely.
