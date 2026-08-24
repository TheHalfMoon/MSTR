# Implementation Plan: MSTR-000 Universal Laptop Qualification + Interaction Contract

**Branch:** `plan/000-speckit-complete-package`  
**Spec:** `specs/000-universal-laptop-interaction-contract/spec.md`  
**Constitution:** `.specify/memory/constitution.md`  
**Status:** Implementation-ready after review

## Summary

MSTR-000 builds a small, cross-platform qualification harness and evidence package that answers expensive questions before long training: actual laptop/distribution floor; legally/technically eligible compact bases; local Q4/runtime viability; trainable prompt/tool/edit/cache contract; fair candidate selection after bounded equivalent adaptation; minimal context stack; trustworthy executable task/verifier factory; and a bounded MSTR-001 proposal.

The implementation separates the **research qualification harness** from the future **end-user MSTR runtime**. MSTR-000 uses Python for fast reproducible experimentation and evidence handling; later Spec Kit workstreams may implement the shipping runtime in Rust or another portable technology after runtime/backbone constraints are empirically known.

## Technical Context

**Primary language:** Python 3.11+  
**Package/build:** `pyproject.toml`; `uv` preferred, standard Python packaging supported  
**CLI:** dependency-light Python CLI  
**Schemas:** JSON Schema Draft 2020-12  
**Persistence:** JSON/JSONL + Markdown summaries; large binaries/logs external and referenced by hash/path  
**Testing:** `pytest`; contract fixtures; deterministic serialization golden tests; offline/network/stale-write tests  
**Static quality:** Ruff + mypy or explicitly accepted equivalents  
**Model/runtime integration:** adapter interfaces; no backend preselected  
**OS qualification:** Windows x86_64, Linux x86_64, macOS arm64/M1-class  
**Primary hardware:** U1 = 8 GB, CPU-only, 8K, reference editor + medium repository open  
**Performance protocol:** `MSTR-MEASURE-v0`  
**Distribution protocol:** `MSTR-DIST-v0`  
**Network default:** disabled/local-only  
**Model files in Git:** prohibited  
**Long training / large-scale RL:** out of scope

### Harness Performance Goals

The harness should add negligible distortion: event timestamp target <1 ms per lifecycle event; deterministic serializer byte stability; ordinary manifest validation target <100 ms; evidence/report generation kept outside TTVC unless explicitly measured; no hidden network calls; platform sampling interval documented.

### Scale / Scope

Designed for ~6–10 statically screened compact candidates, ~3–5 locally admitted artifacts, 3 required OS families, 4K/8K/16K contexts, tens to low hundreds of controlled fixtures, repeated runs/seeds sufficient for selection, and one small environment-factory MVP.

## Constitution Check

| Principle | Compliance | Status |
|---|---|---|
| Universal Laptop | U1 8 GB/CPU/8K is blocking | PASS |
| Local/Accountless/Private | MSTR-DIST-v0; no default network/account/API | PASS |
| Evidence Before Selection | identities + separate score surfaces | PASS |
| Rights Fail Closed | static rights gate before weight access | PASS |
| Freeze Coupled Contracts | Interaction Contract before material SFT/RL | PASS |
| TTVC / Verified Utility | MSTR-MEASURE-v0 drives selection | PASS |
| Smallest Sufficient Architecture | heavy arms comparative only | PASS |
| Evaluation Integrity | private/fresh design + leakage controls | PASS |
| Reproducibility | exact manifests/hashes/failures retained | PASS |
| Bounded Authority | paid/weight/compute actions task-scoped | PASS |

**Pre-design gate:** PASS.  
**Post-design re-check:** PASS. Data model/contracts introduce no cloud dependency, mandatory graph DB, selected backbone, or long-training authority.

## Project Structure

### Spec Kit

```text
.specify/memory/constitution.md
docs/canonical/CURRENT_STATE.md
docs/canonical/PROGRAM_ROADMAP.md
specs/000-universal-laptop-interaction-contract/
  spec.md
  clarification-closeout.md
  research.md
  plan.md
  data-model.md
  quickstart.md
  implementation-handoff.md
  contracts/
  checklists/
  evidence/
  tasks.md
```

### Implementation Created by Tasks

```text
pyproject.toml
src/mstr_qualify/
  cli.py errors.py ids.py schemas.py manifests.py evidence.py rights.py reporting.py
  measurement/
  runtimes/
  interaction/
  context/
  verifier/
  environment/
schemas/
configs/{hardware,candidates,runtimes,interaction,context}/
benchmarks/{manifests,fixtures,private}/
artifacts/{candidates,manifests,results,decisions}/
tests/{unit,contract,integration,fixtures,security}/
```

Not built in MSTR-000: production desktop GUI, large training pipeline, distributed RL stack, model weights in Git, mandatory graph/vector DB, subagent swarm, learned apply model, cloud inference service.

## Architecture

### Qualification CLI

Expected families:

```text
mstr-qualify validate
mstr-qualify rights <candidate-config>
mstr-qualify candidate static <candidate-config>
mstr-qualify manifest validate <manifest>
mstr-qualify artifact verify <artifact-manifest>
mstr-qualify measure <run-manifest>
mstr-qualify report <benchmark-manifest>
mstr-qualify interaction validate <contract>
mstr-qualify context compare <manifest>
mstr-qualify environment validate <task>
```

No generic command silently downloads weights, calls paid APIs, or accesses network.

### Adapter Boundaries

- `RuntimeAdapter`: load/prefill/decode/cache/terminate.
- `ContextProvider`: index/update/query/resource metrics.
- `EditApplier`: validate/apply/reject stale edits.
- `Verifier`: deterministic checks/structured results.
- `PlatformSampler`: memory/paging/CPU/thermal/editor metrics.

### Evidence Pipeline

```text
manifest -> schema validation -> identity resolution -> bounded execution
        -> structured RunEvidence -> JSON/JSONL + human report -> DecisionRecord
```

### Failure Model

Distinguish configuration invalid, rights ineligible/ambiguous, artifact mismatch, runtime unsupported, serialization failure, stale conflict, verifier failure, model failure, tool/infrastructure failure, memory-pressure failure, timeout, benchmark invalidation, and network-policy violation.

## Implementation Phases

0. Spec Kit/governance freeze.
1. Harness foundation: packaging, schemas, identity, CLI, tests.
2. Rights/manifest/static candidate qualification, no weights.
3. Task-scoped local artifact/Q4 qualification after explicit authority.
4. Interaction contract tournament.
5. Candidate quality + equivalent bounded micro-adaptation.
6. Context tournament.
7. Environment/verifier MVP.
8. Security/provenance/leakage controls.
9. MSTR-000 closeout and bounded MSTR-001 proposal.

## Test Strategy

**Unit:** IDs/hashes, schema validation, rights logic, manifest validation, timing, memory classification, stale edits, comparison rules.  
**Contract:** valid/invalid schema fixtures; byte-stable serializers; Interaction Contract snapshots; task/run round trips.  
**Integration:** offline CLI; dummy runtime; subprocess verifier; process measurement; exact search; manifest->execution->evidence->report.  
**Security:** network default-off; workspace traversal; protected evaluator; malicious repo instructions; reward shortcuts; leakage controls.  
**Platform:** OS-specific samplers; unavailable metrics marked unavailable rather than invented.

## Complexity Tracking

| Complexity | Why | Simpler alternative rejected |
|---|---|---|
| Python qualification harness + future product runtime separation | fast research without locking product runtime | build full product runtime first |
| Adapter interfaces | fair backend/context tournaments | hard-code one backend |
| Schemas + Markdown | reproducibility and automated validation | prose-only evidence |
| Environment factory MVP | RL readiness depends on verifier quality | choose RL framework first |
| Private/fresh evaluation | public contamination/noise risk | public leaderboards only |

No additional architecture complexity is approved.

## Authority Boundaries

MSTR-000 tasks may create source, tests, manifests, fixtures, and docs. They do not automatically authorize model-weight acquisition, gated-term acceptance, paid APIs, rented compute, micro-adaptation, long training, large data ingestion, RL, or release. Exact tasks must explicitly grant external effects and state resource/cost ceilings.

## Deliverables at Closeout

Measured hardware/OS floor; distribution/install/privacy contract; local runtime/Q4 baseline; Interaction Contract v1; deterministic apply semantics; minimal context engine; top backbone/top-two pilot; environment MVP requirements; bounded MSTR-001 proposal; independent review; founder acceptance.
