from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
BASE = "5e74e77c1fc86d4ebc7e64654f45bd18f565edd6"
BASE_TREE = "66120bf247e7d9b9da34d5d47603493c8dce4c30"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    target.write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise RuntimeError(f"required anchor missing in {path}: {old[:160]!r}")
    write(path, text.replace(old, new, 1))


def append_once(path: str, marker: str, section: str) -> None:
    text = read(path)
    if marker in text:
        raise RuntimeError(f"duplicate marker in {path}: {marker}")
    write(path, text.rstrip() + "\n\n" + section.strip() + "\n")


# Re-pin the preserved research artifacts to the live upstream revisions reverified
# before this reconstruction. Revision movement alone does not change disposition.
revision_updates = {
    "c389f96a06005300336904239c409258129812c9": "c389f96bf3a9b6807cb71ed6bdad5849be0df6d8",
    "d8563a7d213dd2472c18314992b9435527a11eaf": "04d809ceab9df28f9adaed044884180159172930",
    "a978f8924522bb72c0d5a876b3990d41d432decf": "5c995c365dfb1fd5bc56fda688be5d8538f9931f",
    "2a8d8b739a7be305f570963240f8f96ba62c90d0": "5dc9490bb35f9729ef2c95d00a19ccd30c26339c",
    "dbae8d5667c61f5f4b313b0169d8acd8f102373a": "1891e22b25bda4a4e88e23b3866c3ee7a127e3be",
}

research_path = "specs/002-code-model-supremacy-foundation/research-source-adoption-2026-09-08.md"
research = read(research_path)
for old, new in revision_updates.items():
    if old not in research:
        raise RuntimeError(f"old research revision missing: {old}")
    research = research.replace(old, new)
research = research.replace(
    "Status: PLANNING_RESEARCH_CANDIDATE",
    "Status: CANONICAL_RESEARCH_INPUT_ON_MERGE",
)
write(research_path, research)
append_once(
    research_path,
    "## Revision re-verification on canonical planning base",
    f"""## Revision re-verification on canonical planning base

Planning base: `{BASE}`  
Planning-base tree: `{BASE_TREE}`  
Reverified: 2026-09-08

All 18 upstream refs in this source set were re-read before reconstruction. Thirteen remained at the previously observed immutable revisions. Five moved and are pinned here at their newly observed heads:

- `deepseek-ai/deepseek-harness@master` -> `c389f96bf3a9b6807cb71ed6bdad5849be0df6d8`
- `SWE-agent/mini-swe-agent@main` -> `04d809ceab9df28f9adaed044884180159172930`
- `SWE-agent/SWE-ReX@main` -> `5c995c365dfb1fd5bc56fda688be5d8538f9931f`
- `Aider-AI/aider@main` -> `5dc9490bb35f9729ef2c95d00a19ccd30c26339c`
- `ifm-ai/xllm@main` -> `1891e22b25bda4a4e88e23b3866c3ee7a127e3be`

Revision movement alone does not change a capability disposition. Every future copied or adapted primitive must independently reverify and bind its exact adopted revision in a `SourceAdoptionRecord`; this research snapshot is not mutable runtime dependency authority.""",
)

snapshot_path = "artifacts/manifests/MSTR-source-adoption-research-snapshot-2026-09-08.json"
snapshot = json.loads(read(snapshot_path))
snapshot["status"] = "CANONICAL_PLANNING_RESEARCH_ON_MERGE"
snapshot["canonical_planning_base"] = BASE
snapshot["canonical_planning_base_tree"] = BASE_TREE
snapshot["revision_reverification"] = {
    "reverified_date": "2026-09-08",
    "source_count": 18,
    "unchanged_source_count": 13,
    "changed_source_count": 5,
    "changed_sources": [
        "deepseek-harness",
        "mini-swe-agent",
        "swe-rex",
        "aider",
        "ifm-xllm",
    ],
}
by_id = {item["source_id"]: item for item in snapshot["sources"]}
by_id["deepseek-harness"]["observed_revision"] = revision_updates[
    "c389f96a06005300336904239c409258129812c9"
]
by_id["mini-swe-agent"]["observed_revision"] = revision_updates[
    "d8563a7d213dd2472c18314992b9435527a11eaf"
]
by_id["swe-rex"]["observed_revision"] = revision_updates[
    "a978f8924522bb72c0d5a876b3990d41d432decf"
]
by_id["aider"]["observed_revision"] = revision_updates[
    "2a8d8b739a7be305f570963240f8f96ba62c90d0"
]
by_id["ifm-xllm"]["observed_revision"] = revision_updates[
    "dbae8d5667c61f5f4b313b0169d8acd8f102373a"
]
write(snapshot_path, json.dumps(snapshot, indent=2) + "\n")

strategy_path = "docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md"
replace_once(
    strategy_path,
    "Status: PLANNED_CANONICAL_AMENDMENT_CANDIDATE",
    "Status: CANONICAL_PLANNING_AMENDMENT_ON_MERGE",
)
append_once(
    strategy_path,
    "## 18. Canonical planning-base reconstruction",
    f"""## 18. Canonical planning-base reconstruction

This amendment was reconstructed from exact canonical `main` `{BASE}` rather than rebasing, merging, or cherry-picking the stale planning branch. The three prior research artifacts were treated only as source material, all 18 upstream refs were reverified, and five moved heads were repinned in the companion snapshot.

Completed B014-B030 history remains closed and unchanged. B031 retains its existing exact prerequisites and authority semantics. B032 is the first remaining MSTR-000B task that may freeze these source-adoption interfaces into downstream entry contracts; B033 independently red-teams the resulting design; B034 may close only after those obligations and every earlier canonical requirement are satisfied.

This planning amendment creates no model access, model execution, dataset admission, training, paid compute, external dispatch, or production-release authority.""",
)

# Reconcile the descriptive live-state document without claiming B012 completion.
state_path = "docs/canonical/CURRENT_STATE.md"
replace_once(state_path, "**Checkpoint:** 2026-09-05 Asia/Riyadh", "**Checkpoint:** 2026-09-08 Asia/Riyadh")
replace_once(
    state_path,
    "CANONICAL_MAIN_AT_LATEST_RECONCILIATION = 8916fa7138ad56d18452b7a20db9c8cb982648ba",
    f"CANONICAL_MAIN_AT_LATEST_RECONCILIATION = {BASE}",
)
replace_once(
    state_path,
    "CANONICAL_TREE = b016ab6a3899accc352d8f177a2ba76451259f66",
    f"CANONICAL_TREE = {BASE_TREE}",
)
replace_once(
    state_path,
    "ACTIVE_IMPLEMENTATION_TASK = T031_AUTHORITY_AND_EXECUTION_RECONCILIATION / B012_EXACT_AUTHORITY_GATE / A019_A020_CONVERGENCE_GATES",
    "ACTIVE_IMPLEMENTATION_TASK = T031_AUTHORITY_AND_EXECUTION_RECONCILIATION / B012_EQUIVALENT_QUALIFICATION / B013_BLOCKED_BY_B012 / A019_A020_CONVERGENCE_GATES",
)
replace_once(
    state_path,
    "CURRENT_MSTR_000B_FRONTIERS = B012 / PENDING / BLOCKED_BY_EXACT_FOUNDER_AUTHORITY | B031 / PENDING / TRANSITIVELY_BLOCKED_BY_A019_A020_AND_B013",
    "CURRENT_MSTR_000B_FRONTIERS = B012 / PENDING / AUTHORITY_SATISFIED / EQUIVALENT_QUALIFICATION_INCOMPLETE | B013 / BLOCKED_BY_B012 | B031 / PENDING / TRANSITIVELY_BLOCKED_BY_A019_A020_AND_B013",
)
append_once(
    state_path,
    "## 2026-09-08 Source-adoption and B012 reconciliation",
    f"""## 2026-09-08 Source-adoption and B012 reconciliation

Exact live verification on canonical planning base `{BASE}` established:

```text
B012_CANONICAL_STATE = PENDING
B012_REQUIRED_AUTHORITY = B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION
B012_AUTHORITY_RESULT = SATISFIED
B012_ELIGIBLE_ON_EXACT_MAIN = true
B012_COMPLETE_CANONICAL = false
B013 = BLOCKED_BY_B012
B012_QWEN_PROVENANCE_REPAIR_PR = #187 / MERGED {BASE}
B012_QWEN_FAILED_RECOVERY_RUN = 34163308005 / FAILURE_BEFORE_RAW_CODE
B012_QWEN_FUTURE_RECOVERY = SEPARATELY_GATED / NO_RETRY_OR_DISPATCH_AUTHORITY_CREATED_BY_PR187
SOURCE_CODE_PERMISSION_CREATES_DATA_ADMISSION = false
SOURCE_CODE_PERMISSION_CREATES_MODEL_OR_TRAINING_AUTHORITY = false
```

The older `BLOCKED_BY_EXACT_FOUNDER_AUTHORITY` description is superseded by the canonical authority artifact and exact machine-gate evidence. Authority satisfaction is not B012 completion. PR #187 repaired provenance only and explicitly created no retry or external-dispatch authority. The source-adoption amendment remains planning/governance only and preserves completed B014-B030 history.""",
)

append_once(
    "docs/canonical/PROGRAM_ROADMAP.md",
    "## Source Adoption and Capability Mining Amendment — 2026-09-08",
    """## Source Adoption and Capability Mining Amendment — 2026-09-08

MSTR-000B carries a source-adoption governance lane into its remaining convergence work without reopening completed B014-B030 tasks.

```text
SOURCE_CODE_PERMISSION
  != DATA_ADMISSION
  != MODEL_WEIGHT_AUTHORITY
  != TRAINING_AUTHORITY
  != EXTERNAL_EFFECT_AUTHORITY
```

B031 keeps its existing exact prerequisites. B032 must freeze `SourceAdoptionRecord`, `ExecutionBackendProfile`, `ResumableTaskCheckpoint`, `ImprovementDecisionRecord`, `RepositoryContextIndexProfile`, and `TrainingBackendParityRecord`, plus `MINIMAL_BASH_LINEAR_BASELINE`, baseline-first runtime acceleration, immutable upstream revision/update/rollback governance, and behavioral-reconstruction evaluation. B033 independently red-teams those obligations. B034 cannot close MSTR-000B unless the source-adoption additions are canonical and all earlier task requirements remain satisfied.

Source-derived implementation is downstream and task-bound: the smallest MSTR-native or bounded primitive is preferred, mutable upstream dependencies are rejected from the baseline, and every actual copied/adapted primitive requires provenance, license/NOTICE, dependency, security, equivalence, footprint, update, and rollback evidence before merge.""",
)

append_once(
    "docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md",
    "## Source-Derived Harness and Research Primitives",
    """## Source-Derived Harness and Research Primitives

Source-derived harness capability must earn its complexity. `MINIMAL_BASH_LINEAR_BASELINE` is the anti-complexity control for any richer harness/runtime surface. Promotion compares verifier-correct completion/DVCR, TTVC, LOC, dependency count, prompt/tool token overhead, startup latency, RSS, attack surface, portability, recovery burden, and deterministic replay.

Downstream harness work must use explicit records where applicable:

- `ExecutionBackendProfile` for process/session/timeout/cancellation/reset/streaming/isolation/fallback semantics;
- `ResumableTaskCheckpoint` for small secret-free durable task state that never becomes authority;
- `ImprovementDecisionRecord` for immutable `KEEP | DISCARD | CRASH | INCONCLUSIVE` optimization history with protected evaluator separation;
- `RepositoryContextIndexProfile` for the staged `grep/find -> syntax/symbol -> token-budgeted repository map -> learned only when justified` context ladder.

Every copied or adapted primitive additionally requires a `SourceAdoptionRecord`. No source repository, benchmark claim, runtime, network service, or dependency is admitted by citation or source-use permission alone.""",
)

append_once(
    "docs/canonical/CODE_MODEL_SUPREMACY_STRATEGY.md",
    "## Source Capability Mining and Reconstruction Discipline",
    """## Source Capability Mining and Reconstruction Discipline

MSTR may selectively mine useful implementation primitives, but model quality and product claims remain MSTR-evidence-only. Source-code permission does not admit source repositories as training/evaluation data and does not create model, training, compute, or external-effect authority.

The capability-mining order is fail-closed:

```text
SMALLEST_MSTR_NATIVE_INVARIANT
-> BOUNDED_PINNED_SOURCE_PRIMITIVE_WITH_SOURCE_ADOPTION_RECORD
-> PINNED_OPTIONAL_DEPENDENCY_WITH_NARROW_ADAPTER
-> WHOLE_REPOSITORY_ONLY_IF_NO_SMALLER_EQUIVALENT_EXISTS
```

Runtime acceleration is baseline-first: ordinary autoregressive reference, then compatible native acceleration already present in the pinned runtime, then custom/source-derived acceleration only when exact MSTR evidence proves the native path insufficient. Behavioral reconstruction becomes a distinct evaluation lane with evaluator-owned hidden tests. Donor benchmark and speed claims remain research signals rather than MSTR results.""",
)

append_once(
    "docs/canonical/TRAINING_EXECUTION_STRATEGY.md",
    "## Training Backend Parity Before Acceleration Promotion",
    """## Training Backend Parity Before Acceleration Promotion

An accelerated training backend such as Unsloth may not become canonical merely because it is faster or uses less memory. After a separate training authority exists, backend promotion requires a `TrainingBackendParityRecord` against the reference path under equal model revision, data manifest, seed, update budget, objective, export path, and evaluation identity.

The parity record binds trainable parameter set/count, optimizer and scheduler semantics, loss trajectory tolerance, checkpoint/resume behavior, merged-artifact identity or declared numerical tolerance, post-merge inference behavior, Q4 conversion where applicable, peak memory, wall time, and unexplained divergences. Unexplained semantic or artifact divergence fails closed.

This planning rule creates no training, model access, paid compute, or dataset-ingestion authority.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/spec.md",
    "### FR-030 — Governed source adoption and capability mining",
    """### FR-030 — Governed source adoption and capability mining

B032 MUST freeze a fail-closed source-adoption design that keeps source-code permission distinct from data admission, model-weight authority, training authority, and every external-effect authority. Any copied, adapted, vendored, or behaviorally reimplemented core primitive MUST require a `SourceAdoptionRecord` binding immutable upstream revision, permission provenance, license/NOTICE obligations, exact source/method scope, direct/transitive dependencies, external surfaces, offline/privacy behavior, product footprint, integration identity, behavior/equivalence tests, security/evaluator-isolation review, update policy, and rollback.

B032 MUST also carry `MINIMAL_BASH_LINEAR_BASELINE`, `ExecutionBackendProfile`, `ResumableTaskCheckpoint`, `ImprovementDecisionRecord`, `RepositoryContextIndexProfile`, `TrainingBackendParityRecord`, baseline-first runtime acceleration, and behavioral-reconstruction evaluation into the appropriate downstream workstreams without executing those external effects.

B033 MUST independently red-team hidden authority expansion, source/data/model permission conflation, mutable upstream dependencies, license/NOTICE loss, transitive assets, dependency bloat, checkpoint secret leakage, stale context indexes, optimizer/evaluator leakage, non-equivalent accelerated training, source-derived runtime attribution, and rollback failure.

### Source-adoption acceptance addition

MSTR-000B closeout additionally requires that B032 has made the source-adoption obligations canonical and B033 has independently resolved every material source-adoption finding. Completed B014-B030 work remains historical and is not reopened by this amendment.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/research.md",
    "## 15. Source Adoption and Capability Mining Update — 2026-09-08",
    """## 15. Source Adoption and Capability Mining Update — 2026-09-08

The canonical companion research is `research-source-adoption-2026-09-08.md` with machine-readable snapshot `artifacts/manifests/MSTR-source-adoption-research-snapshot-2026-09-08.json`.

The update adds engineering-method evidence from LoopForge, SkillHone, DeepSeek Harness, mini-swe-agent, SWE-ReX, aider, IFM xLLM/horizon-post-train/Uno, AngelSlim, llama.cpp, Unsloth, SelfCodeAlign, SWE-RL, ProgramBench, FEA-Bench, CodeClash, and autoresearch. These sources are donors, controls, or method references only. No source repository, dataset, model, benchmark score, dependency, or external service is admitted by citation alone.

The main gap found is governance around selective source reuse: MSTR requires immutable source adoption records, an anti-complexity baseline, execution-backend and resumability contracts, optimizer/evaluator-separated improvement records, staged repository indexing, training-backend parity, baseline-first acceleration, and rollback-safe upstream refreshes.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/plan.md",
    "## 21. Source Adoption and Capability Mining Amendment — 2026-09-08",
    """## 21. Source Adoption and Capability Mining Amendment — 2026-09-08

This amendment is planning/governance only and does not reopen B014-B030. B031 retains its exact existing dependency graph. B032 is extended to freeze the source-adoption interfaces and route them downstream; B033 independently red-teams them; B034 consumes their resolved canonical evidence.

### 21.1 Minimal primitive and provenance order

```text
MSTR_NATIVE_MINIMAL
-> BOUNDED_PINNED_ADAPTATION
-> PINNED_OPTIONAL_DEPENDENCY
-> WHOLE_REPOSITORY_ONLY_WITH_INDEPENDENT_JUSTIFICATION
```

Mutable branch dependencies, install-time source fetches, and runtime auto-update are prohibited from the baseline path. A `SourceAdoptionRecord` is a merge prerequisite for any source-derived core primitive.

### 21.2 Anti-complexity and harness/runtime records

Every richer harness/runtime proposal is compared with `MINIMAL_BASH_LINEAR_BASELINE`. Downstream design freezes `ExecutionBackendProfile`, `ResumableTaskCheckpoint`, `ImprovementDecisionRecord`, and `RepositoryContextIndexProfile` before implementation. Checkpoints are state, not authority; optimizer-visible and evaluator-protected evidence remain separated.

### 21.3 Training/runtime acceleration

A future accelerated training backend requires `TrainingBackendParityRecord` under separately authorized execution. Runtime acceleration progresses from ordinary reference to native pinned-runtime features before custom/source-derived techniques. Vendor throughput is never MSTR TTVC evidence without exact reproduction.

### 21.4 Behavioral reconstruction

Add a bounded behavioral-reconstruction evaluation lane with evaluator-owned hidden tests and permitted observable behavior. It complements, rather than replaces, repository evolution, feature, greenfield, and Direction-to-Done evidence.

### 21.5 Constitution re-check

The amendment preserves universal-laptop, offline/private, evidence-first, rights/provenance, smallest-sufficient-architecture, evaluation-integrity, reproducibility, and bounded-authority principles. Result: `PASS_FOR_PLANNING`; no constitution amendment is required.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/data-model.md",
    "## 19. SourceAdoptionRecord and source-derived planning records",
    """## 19. SourceAdoptionRecord and source-derived planning records

B032 freezes design-level records for downstream implementation. Their presence in this data model creates no runtime or external-effect authority.

```text
SourceAdoptionRecord
- source_id
- upstream_repository
- upstream_url
- observed_revision
- adopted_revision
- source_use_permission_provenance
- license_identity
- notice_attribution_obligations[]
- source_paths_or_method_references[]
- adoption_mode
- consuming_task
- adoption_reason
- rejected_simpler_alternatives[]
- direct_dependencies[]
- transitive_dependencies[]
- network_filesystem_subprocess_container_gpu_secret_surfaces
- offline_privacy_behavior
- installed_bytes_delta
- startup_latency_delta
- steady_rss_delta
- integration_tree_or_patch_hash
- behavior_equivalence_evidence[]
- security_review
- evaluator_isolation_review
- update_policy
- rollback_target
- data_authority
- model_authority
- training_authority
- external_effect_authority
```

```text
ExecutionBackendProfile
ResumableTaskCheckpoint
ImprovementDecisionRecord
RepositoryContextIndexProfile
TrainingBackendParityRecord
```

The detailed required fields and invariants are governed by `docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md`. Missing provenance, rights, behavior/equivalence, security, evaluator-isolation where relevant, footprint, update, rollback, or exact external-effect authority fails closed.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/contracts/README.md",
    "## Planned by B032 — source adoption governance",
    """## Planned by B032 — source adoption governance

B032 must freeze downstream contracts or equivalent machine-readable records for:

```text
mstr.source-adoption-record.v0
mstr.execution-backend-profile.v0
mstr.resumable-task-checkpoint.v0
mstr.improvement-decision.v0
mstr.repository-context-index-profile.v0
mstr.training-backend-parity.v0
```

These names are planning obligations, not runtime authority before B032 implementation. `SourceAdoptionRecord` must fail closed when immutable source revision, source-use provenance, license/NOTICE, dependency surface, behavior/equivalence evidence, update/rollback, or required external-effect authority is unresolved. `ResumableTaskCheckpoint` explicitly cannot carry or create authority. `ImprovementDecisionRecord` keeps protected evaluator evidence unavailable to the optimizer before candidate proposal. `TrainingBackendParityRecord` does not authorize training.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/quickstart.md",
    "## Source Adoption Downstream Handoff",
    """## Source Adoption Downstream Handoff

No source-derived capability is implemented merely because this amendment is canonical. When B032 becomes eligible it must freeze the source-adoption records and route them to the exact downstream workstream.

Before any source-derived core merge:

```text
immutable upstream revision
-> SourceAdoptionRecord
-> license/NOTICE + transitive dependency review
-> behavior/equivalence tests
-> security/evaluator-isolation review where relevant
-> anti-complexity comparison against MINIMAL_BASH_LINEAR_BASELINE
-> footprint/offline/privacy evidence
-> update + rollback plan
-> exact external-effect authority if any
-> independent review
-> exact-head premerge
-> guarded merge
-> postmerge verification
```

Source-use permission never substitutes for data, model, training, network, compute, or release authority.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/checklists/implementation-readiness.md",
    "## Before B032 Source-Adoption Freeze",
    """## Before B032 Source-Adoption Freeze

- [ ] B031 is `COMPLETE_CANONICAL` and exact B032 eligibility is `true`.
- [ ] `docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md` is canonical.
- [ ] The 2026-09-08 source snapshot pins every reverified upstream revision and records no external-effect authority.
- [ ] B032 freezes `SourceAdoptionRecord` and the five supporting source-derived planning records.
- [ ] `MINIMAL_BASH_LINEAR_BASELINE` is the anti-complexity control for richer harness/runtime proposals.
- [ ] Source permission, data admission, model authority, training authority, and external-effect authority remain distinct.
- [ ] Mutable upstream runtime dependencies and automatic source refresh remain disallowed in the baseline.
- [ ] B033 independently red-teams license/NOTICE, transitive assets, evaluator leakage, dependency bloat, stale indexes, secret leakage, backend parity, and rollback failure.

These checks add obligations to B032/B033; they do not reopen B014-B030 or make B032 executable before B031.""",
)

append_once(
    "specs/002-code-model-supremacy-foundation/implementation-handoff.md",
    "## Source Adoption Amendment Handoff",
    """## Source Adoption Amendment Handoff

Also read `docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md` and `research-source-adoption-2026-09-08.md` before B032/B033 work. The amendment is planning-only until the exact remaining task is eligible.

B031 remains unchanged. B032 freezes the source-adoption governance and downstream interface obligations. B033 independently red-teams them. B034 consumes the resolved results. No source code may enter the MSTR core merely because the donor repository appears in the research matrix.""",
)

# Extend only the still-pending convergence tasks. B031 prerequisites are intentionally untouched.
tasks_path = "specs/002-code-model-supremacy-foundation/tasks.md"
old_b032 = """- [ ] **B032 Amend MSTR-001/MSTR-002/MSTR-003 entry requirements and downstream acceleration obligations.**
  Prerequisite: B031 `COMPLETE_CANONICAL`. Consume `docs/canonical/MSTR_FRONTIER_ACCELERATION_STRATEGY.md` and the canonical B013 frontier snapshot. MSTR-001 consumes Data Constitution, language mix, software evolution, frontier curriculum, checkpoint-lineage substrate experiments where applicable, early low-bit compatibility evidence, and mandatory Q4 promotion. MSTR-002 consumes self-alignment, teacher policy, verifier health, test generation, greenfield/feature and production-compatible same-loop trajectories including failure/negative examples. MSTR-003 consumes frontier curriculum, admitted environments, verifier health, multi-fidelity RL promotion, dynamic synthetic environment generation, previous-MSTR bootstrap with independent admission, targeted trajectory-feedback research, and reward-shortcut controls. The downstream roadmap amendment MUST also carry the non-executing consequences for MSTR-004 (Q4 anchor plus Q3/Q2/structured-ternary, kernel, speculation/parallel-generation, and FAST/NORMAL/DEEP effort-control tournament) and MSTR-006 (sealed anti-leakage headline qualification). B032 itself authorizes none of those external effects.
  Outputs: roadmap/training strategy/preplan amendments, `evidence/mstr-000b/B032-downstream-contracts.md`.
"""
new_b032 = """- [ ] **B032 Amend MSTR-001/MSTR-002/MSTR-003 entry requirements and downstream acceleration/source-adoption obligations.**
  Prerequisite: B031 `COMPLETE_CANONICAL`. Consume `docs/canonical/MSTR_FRONTIER_ACCELERATION_STRATEGY.md`, `docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md`, the canonical B013 frontier snapshot, and the 2026-09-08 source-adoption research snapshot. MSTR-001 consumes Data Constitution, language mix, software evolution, frontier curriculum, checkpoint-lineage substrate experiments where applicable, early low-bit compatibility evidence, mandatory Q4 promotion, and `TrainingBackendParityRecord` before any accelerated training backend promotion. MSTR-002 consumes self-alignment, teacher policy, verifier health, test generation, greenfield/feature and production-compatible same-loop trajectories including failure/negative examples. MSTR-003 consumes frontier curriculum, admitted environments, verifier health, multi-fidelity RL promotion, dynamic synthetic environment generation, previous-MSTR bootstrap with independent admission, targeted trajectory-feedback research, and reward-shortcut controls. B032 MUST also freeze `SourceAdoptionRecord`, `ExecutionBackendProfile`, `ResumableTaskCheckpoint`, `ImprovementDecisionRecord`, `RepositoryContextIndexProfile`, `TrainingBackendParityRecord`, `MINIMAL_BASH_LINEAR_BASELINE`, immutable upstream revision/update/rollback governance, baseline-first runtime acceleration, and behavioral-reconstruction evaluation, then route each to the exact downstream workstream without implementing ineligible external effects. The downstream roadmap amendment MUST carry the non-executing consequences for MSTR-004 (Q4 anchor plus Q3/Q2/structured-ternary, kernel, speculation/parallel-generation, FAST/NORMAL/DEEP effort-control, and source-derived acceleration only after native pinned-runtime baselines) and MSTR-006 (sealed anti-leakage headline and behavioral-reconstruction qualification). B032 itself authorizes none of those external effects and does not reopen B014-B030.
  Outputs: roadmap/training strategy/preplan/source-adoption contract amendments, `evidence/mstr-000b/B032-downstream-contracts.md`.
"""
replace_once(tasks_path, old_b032, new_b032)
old_b033 = """- [ ] **B033 Independent consistency/red-team review.**  
  Prerequisite: B032 `COMPLETE_CANONICAL`. Review frontier freshness/candidate omission, candidate fairness, data leakage, future-Git-history/public-solution/network leakage, rights, reward hacking/evaluator extraction, task-gate bypass, teacher contamination, tokenizer comparability, mandatory Q4 promotion, low-bit quality claims, hardware-specific speed/runtime claims, speculative/parallel-generation attribution, WePLD attribution, and 8GB product preservation. Confirm that no experimental sub-Q4 artifact can replace the required Q4 promotion anchor and that vendor benchmark/speed claims are not represented as MSTR evidence without exact reproduction. Resolve all material findings.
  Outputs: `evidence/mstr-000b/B033-independent-review.md`.
"""
new_b033 = """- [ ] **B033 Independent consistency/red-team review.**  
  Prerequisite: B032 `COMPLETE_CANONICAL`. Review frontier freshness/candidate omission, candidate fairness, data leakage, future-Git-history/public-solution/network leakage, rights, reward hacking/evaluator extraction, task-gate bypass, teacher contamination, tokenizer comparability, mandatory Q4 promotion, low-bit quality claims, hardware-specific speed/runtime claims, speculative/parallel-generation attribution, WePLD attribution, and 8GB product preservation. Independently red-team source adoption for hidden authority expansion; source/data/model/training permission conflation; mutable-upstream dependencies; license/NOTICE or attribution loss; transitive assets/data; dependency bloat; stale or non-deterministic repository indexes; checkpoint secret leakage; optimizer access to protected evaluation; non-equivalent accelerated training; source-derived runtime attribution; missing behavior/equivalence evidence; and rollback failure. Confirm that no experimental sub-Q4 artifact can replace the required Q4 promotion anchor, no donor/vendor benchmark or speed claim is represented as MSTR evidence without exact reproduction, and completed B014-B030 history was not reopened. Resolve all material findings.
  Outputs: `evidence/mstr-000b/B033-independent-review.md`.
"""
replace_once(tasks_path, old_b033, new_b033)
replace_once(
    tasks_path,
    "WEIGHT_CHANGING_TRAINING_AUTHORIZED_BY_THIS_WORKSTREAM = YES\n",
    "WEIGHT_CHANGING_TRAINING_AUTHORIZED_BY_THIS_WORKSTREAM = YES\nSOURCE_CODE_PERMISSION_CONFLATED_WITH_DATA_MODEL_TRAINING_OR_EXTERNAL_AUTHORITY = YES\nSOURCE_DERIVED_CORE_CODE_WITHOUT_SOURCE_ADOPTION_RECORD = YES\nMUTABLE_UPSTREAM_RUNTIME_DEPENDENCY_IN_BASELINE = YES\nSOURCE_ADOPTION_WITHOUT_LICENSE_NOTICE_DEPENDENCY_EQUIVALENCE_OR_ROLLBACK_REVIEW = YES\n",
)

# Exact source-adoption planning contract. It protects historical terminal tasks and
# prevents the amendment from silently widening B031 or external authority.
test_path = "tests/contract/test_source_adoption_planning_contracts.py"
write(
    test_path,
    f'''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "{BASE}"


def _load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_source_snapshot_is_bounded_and_reverified() -> None:
    snapshot = _load_json("artifacts/manifests/MSTR-source-adoption-research-snapshot-2026-09-08.json")
    assert snapshot["canonical_planning_base"] == BASE
    assert snapshot["revision_reverification"]["source_count"] == 18
    assert snapshot["revision_reverification"]["changed_source_count"] == 5
    assert len(snapshot["sources"]) == 18
    assert snapshot["authority_boundary"] == {{
        "source_code_permission_is_data_admission": False,
        "source_code_permission_is_model_weight_authority": False,
        "source_code_permission_is_training_authority": False,
        "source_code_permission_is_external_effect_authority": False,
        "model_access": "NONE",
        "model_execution": "NONE",
        "training": False,
        "paid_cost_usd": 0.0,
    }}
    revisions = {{item["source_id"]: item["observed_revision"] for item in snapshot["sources"]}}
    assert revisions["deepseek-harness"] == "c389f96bf3a9b6807cb71ed6bdad5849be0df6d8"
    assert revisions["mini-swe-agent"] == "04d809ceab9df28f9adaed044884180159172930"
    assert revisions["swe-rex"] == "5c995c365dfb1fd5bc56fda688be5d8538f9931f"
    assert revisions["aider"] == "5dc9490bb35f9729ef2c95d00a19ccd30c26339c"
    assert revisions["ifm-xllm"] == "1891e22b25bda4a4e88e23b3866c3ee7a127e3be"


def test_completed_b_tasks_stay_closed_and_b031_dependencies_do_not_change() -> None:
    catalog = _load_json("configs/task-gate/mstr-000b.json")["tasks"]
    for number in range(14, 31):
        assert catalog[f"B{{number:03d}}"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert catalog["B031"]["canonical_state"] == "PENDING"
    assert catalog["B031"]["prerequisites"] == [
        "A019", "A020", "B002", "B003", "B004", "B015", "B017", "B019",
        "B021", "B023", "B024", "B025", "B027", "B028", "B029", "B030",
    ]
    assert catalog["B032"]["prerequisites"] == ["B031"]
    assert catalog["B033"]["prerequisites"] == ["B032"]


def test_pending_tasks_carry_source_adoption_obligations_without_authority() -> None:
    tasks = (ROOT / "specs/002-code-model-supremacy-foundation/tasks.md").read_text(encoding="utf-8")
    strategy = (ROOT / "docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md").read_text(encoding="utf-8")
    for token in [
        "SourceAdoptionRecord",
        "ExecutionBackendProfile",
        "ResumableTaskCheckpoint",
        "ImprovementDecisionRecord",
        "RepositoryContextIndexProfile",
        "TrainingBackendParityRecord",
        "MINIMAL_BASH_LINEAR_BASELINE",
    ]:
        assert token in tasks
        assert token in strategy
    assert "B032 itself authorizes none of those external effects" in tasks
    assert "does not reopen B014-B030" in tasks
    assert "SOURCE_CODE_PERMISSION" in strategy
    assert "DATA_ADMISSION" in strategy
    assert "MODEL_WEIGHT_AUTHORITY" in strategy
    assert "TRAINING_AUTHORITY" in strategy
    assert "EXTERNAL_EFFECT_AUTHORITY" in strategy


def test_b012_reconciliation_does_not_claim_completion_or_retry_authority() -> None:
    state = (ROOT / "docs/canonical/CURRENT_STATE.md").read_text(encoding="utf-8")
    assert "B012_CANONICAL_STATE = PENDING" in state
    assert "B012_AUTHORITY_RESULT = SATISFIED" in state
    assert "B012_COMPLETE_CANONICAL = false" in state
    assert "B012_QWEN_FUTURE_RECOVERY = SEPARATELY_GATED" in state
''',
)
