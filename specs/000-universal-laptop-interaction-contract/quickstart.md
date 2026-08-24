# MSTR-000 Quickstart

## Read in Order
1. `AGENTS.md`
2. `.specify/memory/constitution.md`
3. `docs/canonical/CURRENT_STATE.md`
4. `docs/canonical/PROGRAM_ROADMAP.md`
5. `spec.md`
6. `clarification-closeout.md`
7. `research.md`
8. `plan.md`
9. `data-model.md`
10. `contracts/README.md`
11. `checklists/implementation-readiness.md`
12. `tasks.md`
13. `implementation-handoff.md`

## Authority Check
Identify the next incomplete task and whether it explicitly authorizes model weights, paid API, rented compute, large data, training, or network. If not explicitly authorized, it remains prohibited. T000–T002 are canonical complete.

## Branching
Use focused branches like `task/000-t003-harness-bootstrap`. No force-push/destructive rewrite required.

## Initial Harness
T003+ creates `pyproject.toml`, `src/mstr_qualify/`, `schemas/`, `tests/`, `configs/`, `benchmarks/`, `artifacts/`. Model binaries, large logs/caches/environments are not committed.

## Contributor Setup
Python 3.11+. Preferred: `uv sync --dev && uv run pytest -q`; standard Python packaging/testing must remain possible.

## Expected CLI
`python -m mstr_qualify validate`, `rights`, `candidate static`, `manifest validate`, later explicitly authorized artifact/measure commands. No command silently downloads weights.

## Contract Loop
Implement schema -> valid fixture -> invalid fixtures -> deterministic/round-trip tests -> focused tests -> full tests -> task evidence.

## Weight Boundary
First weight-access task must define candidate list, exact revisions, hash verification, storage ceiling, quant/runtime, network source, cost, destination, cleanup. Do not infer authority from tournament existence.

## Measurement
Use `MSTR-MEASURE-v0`. Never compare mismatched cold/warm, verifier tier, task manifest, timeout, hardware class, context/cache as equivalent.

## Before PR Merge
Verify exact head, diff scope, focused/full tests, no unexpected network/model/paid action, schema-valid outputs, current-state/task updates supported by evidence, no false CI claim.

## Exit
MSTR-001 long training stays blocked until mandatory closeout + independent review + founder acceptance + canonical bounded MSTR-001 proposal.
