# Feature Specification: MSTR-000 Universal Laptop Qualification + Interaction Contract

**Feature Branch:** `plan/000-speckit-complete-package`  
**Created:** 2026-08-24  
**Status:** Ready for implementation after review  
**Input:** Build the preconstruction qualification program that determines the smallest viable model/runtime/distribution contract for a best-in-class local software-engineering system that ordinary laptop users can install and run.

## User Scenarios & Testing

### User Story 1 - Ordinary Laptop User Can Acquire and Run MSTR Locally (Priority: P1)

A developer with an ordinary contemporary laptop can obtain the primary MSTR release, install or launch it without a development toolchain, open a repository, and use local coding assistance without a discrete GPU, provider account, API key, subscription, activation server, or mandatory network connection after artifact acquisition.

**Why this priority:** This is the product identity. A stronger model that requires workstation/cloud hardware fails the primary MSTR mission.

**Independent Test:** On each required U1 platform lane, use a fully local artifact set, disconnect external networking, launch basic MSTR without Docker/Python/Node.js, open the reference repository in the reference editor, and complete the local smoke interaction without OOM, sustained swap thrashing, provider authentication, or remote inference.

**Acceptance Scenarios:**
1. Given an 8 GB U1 machine with all artifacts local, when network is disconnected and MSTR launches, basic assistance starts without provider auth or remote fallback.
2. Given editor + medium repo are open, when MSTR operates at 8K, whole-laptop responsiveness remains within canonical guardrails.
3. Given no Python/Node/Docker/compiler toolchain, primary install still launches basic MSTR.
4. At least one official complete acquisition path is accountless/ungated where redistribution rights permit.

### User Story 2 - Researcher Can Qualify Backbone Candidates Reproducibly (Priority: P1)

A researcher can statically screen compact foundation candidates, admit only legally/distributably compatible models, build/obtain pinned artifacts under explicit task authority, and compare them under the same hardware, quantization, measurement, manifest, and reporting contracts.

**Independent Test:** run static-only qualification on one candidate and produce a schema-valid candidate record with exact revision, rights decision, architecture/tokenizer metadata, runtime/quantization maturity, and admission decision without downloading weights.

**Acceptance Scenarios:** ambiguous/non-commercial rights fail closed; incompatible required components block primary PASS; mismatched cache/manifests cannot be presented as fair direct comparison; new eligible models can enter through the same gate.

### User Story 3 - Engineer Can Use a Stable Interaction and Edit Contract (Priority: P1)

An engineer can rely on one versioned prompt/tool/edit/cache contract that is deterministic enough to train against, cache efficiently, apply edits safely, and migrate deliberately.

**Independent Test:** canonical fixtures round-trip byte-stably; schema validation works; stale writes reject deterministically.

**Acceptance Scenarios:** stale hash never silently overwrites; identical tool results serialize identically; malformed tool output fails explicitly; material post-training contract revision requires migration evidence.

### User Story 4 - Researcher Can Select the Best Universal-Laptop Backbone by Verified Utility (Priority: P1)

Surviving candidates are compared by raw coding, FIM, tool/edit reliability, repo work, local Q4, verified completion, TTVC, memory, sustained responsiveness, and equivalent bounded adaptation.

**Independent Test:** regenerate a scorecard from exact evidence identities with raw/neutral/full-system separation.

**Acceptance Scenarios:** a high leaderboard model failing U1 cannot win; Q4 primary behavior controls viability; post-adaptation evidence can change rank; harness-only gain is attributed to system layer.

### User Story 5 - Runtime Engineer Can Choose the Smallest Useful Context Engine (Priority: P2)

Compare exact search, symbols, sparse indexing, embeddings/rerankers, SCIP, Graphify, and Code-Graph-RAG under the same tasks and choose the smallest solve-rate/token/latency/RAM/disk Pareto-efficient stack.

**Independent Test:** each arm reports localization, solve rate, tokens, TTVC, RAM, disk, build/update cost.

### User Story 6 - RL/Data Engineer Can Build Verifiable Executable Tasks Safely (Priority: P2)

Construct executable tasks with reproducible environments, reference-pass/no-op-fail/unsolved checks, reward-shortcut attacks, provenance, and reset metrics before large RL planning.

**Independent Test:** one fixture passes reference, fails no-op/unsolved, and rejects evaluator tampering/test deletion/hardcoding shortcuts.

### User Story 7 - Security and Provenance Reviewer Can Audit the Entire Qualification Chain (Priority: P2)

A reviewer can trace every material score/artifact/rights/provenance/security boundary to exact records without chat history.

**Independent Test:** traverse report -> run -> task -> model/artifact/runtime/hardware/contract/provenance and reject missing mandatory identity.

### User Story 8 - Founder Can Close MSTR-000 With an Implementation-Ready MSTR-001 Decision (Priority: P1)

The founder receives one reconciled decision package containing measured laptop floor, contracts, local runtime/Q4, context decision, top backbone/top-two, risks, and bounded next-stage proposal.

**Independent Test:** a new agent can state exactly what is selected, authorized, deferred, and prohibited.

## Edge Cases

- Small active params but huge total weights.
- Permissive backbone with restrictive tokenizer/vision component.
- Upstream license/files change between static check and weight access.
- Q4 fits disk but KV cache breaks 8 GB at 8K.
- Burst CPU looks fast but thermal throttling ruins sustained use.
- Fast Metal path but no portable Windows/Linux CPU path.
- Tokenizer makes tokens/sec misleading.
- Retrieval helps solve rate but destroys RAM/disk/latency budget.
- Tool JSON is syntactically valid but semantically unauthorized.
- Verifier is exploitable by test deletion/assertion weakening/hardcoding.
- Benchmark fixes leak via training/git/cache/network.
- Paid comparison model/harness changes mid-run.
- Task succeeds without edit (`TTFCE=N/A`).
- Agent training destroys FIM/raw coding/Q4/tool reliability.
- Vision footprint breaks universal product.

## Functional Requirements

### Product and Platform
- **FR-001:** U1 MUST be 8 GB total RAM, CPU-only, 8K, OS + editor + medium repo + MSTR concurrently.
- **FR-002:** 4K/8K/16K contexts MUST be characterized separately.
- **FR-003:** Primary Q4 artifact target MUST be <=3 GB unless explicitly amended by measured governance.
- **FR-004:** Windows x86_64, Linux x86_64, and macOS arm64/M1-class MUST be required lanes.
- **FR-005:** Final support floor MUST be measurement-based, not vendor claims.
- **FR-006:** Whole-laptop usability MUST include memory, paging, sustained CPU, and editor responsiveness.

### Distribution, Install, Privacy
- **FR-007:** No provider account/API key/subscription/activation/remote fallback for primary local use.
- **FR-008:** At least one official complete acquisition path MUST be ungated/accountless where rights allow.
- **FR-009:** Basic operation MUST work offline after required artifacts are local.
- **FR-010:** Telemetry/outbound network MUST be off by default.
- **FR-011:** User code MUST NOT be uploaded/used for training by default.
- **FR-012:** Basic launch MUST NOT require Docker/Python/Node/compiler/source build.
- **FR-013:** Required artifacts MUST have compatibility metadata and cryptographic hashes.

### Candidate Admission and Rights
- **FR-014:** Every candidate MUST be pinned to an exact upstream revision before weight access.
- **FR-015:** Admission MUST fail closed unless intended personal/commercial use, modification/fine-tuning, quantization/conversion, and derivative redistribution are sufficiently established.
- **FR-016:** Dataset, teacher/API-output, runtime, tokenizer/vision, and tooling rights MUST be separate records.
- **FR-017:** Research/non-commercial/field/scale-restricted candidates MUST NOT become primary unless resolved.
- **FR-018:** Landscape MUST be rescanned immediately before first weight access.

### Evidence and Measurement
- **FR-019:** Material results MUST use a versioned measurement protocol.
- **FR-020:** Evidence MUST bind model revision, artifact hash, tokenizer, quantizer, runtime, hardware, context/cache, interaction contract, task manifest, seed, result.
- **FR-021:** TTFI/TTFA/TTFCE/TTVC, solve rate, memory/paging, sustained throughput, responsiveness MUST follow canonical definitions.
- **FR-022:** Cold/session-warm/prefix-warm results MUST be separate.
- **FR-023:** Failed/timeout/OOM/verifier-fail runs MUST remain evidence.
- **FR-024:** Raw/neutral/full-system scores MUST be separate.
- **FR-025:** Direct comparisons MUST reject mismatched protocols/manifests/config unless labeled non-equivalent.

### Interaction and Editing
- **FR-026:** Prompt/chat, FIM, tool grammar, result serialization, edit grammar, context order, stale-write, serving/cache MUST be versioned before material agent SFT/RL.
- **FR-027:** Tool/result serialization MUST be deterministic.
- **FR-028:** Edit layer MUST be stale-safe.
- **FR-029:** v1 apply path MUST be deterministic; learned apply not required.
- **FR-030:** Malformed/rejected tool calls MUST NOT count as successful actions.

### Candidate Tournament
- **FR-031:** Initial static qualification MUST include the clarified candidate set and lower-bound control.
- **FR-032:** Surviving candidates MUST be tested in required local Q4-class form.
- **FR-033:** Selection MUST include raw coding, FIM, multilingual instructions, tool/edit, repo work, TTVC, solve rate, memory, sustained responsiveness.
- **FR-034:** Vendor benchmarks MUST NOT be sufficient for selection.
- **FR-035:** Finalists MUST receive equivalent bounded adaptation unless ineligible/dominated before adaptation.
- **FR-036:** Rights/U1/distribution failures MUST block primary selection regardless of quality.

### Context Engine
- **FR-037:** Exact search MUST be baseline.
- **FR-038:** Tree-sitter symbols and sparse indexing MUST be measured before heavier default retrieval.
- **FR-039:** Embeddings, SCIP, Graphify, Code-Graph-RAG MUST remain optional until proven.
- **FR-040:** Context RAM/disk/startup/update costs MUST count against laptop budget.
- **FR-041:** Default MUST be smallest measured Pareto-efficient stack.

### Environment / Verifier Factory
- **FR-042:** Executable tasks MUST prove reference/oracle pass and no-op fail before RL use.
- **FR-043:** Tasks MUST support unsolved/broken validation where applicable.
- **FR-044:** Shortcut tests MUST cover evaluator/test tampering, deletion/weakening, hardcoding, output spoofing, future history, cache/deleted solution recovery, public-solution/network leakage.
- **FR-045:** Reset latency, yield, reproducibility, CPU, storage, failure rate MUST be measured before RL scaling.

### Security and Provenance
- **FR-046:** Repository content MUST be treated as untrusted data.
- **FR-047:** Secret/workspace/network semantics MUST be explicit/tested.
- **FR-048:** Training provenance MUST support source, license, hash, dedup lineage, benchmark exclusion, opt-out.
- **FR-049:** Benchmark runtime MUST prevent future-history/public-solution retrieval.
- **FR-050:** Public benchmark limitations/contamination risk MUST accompany headline evaluation.

### Governance and Closeout
- **FR-051:** GitHub main MUST remain canonical.
- **FR-052:** Weight access, paid APIs, rented compute, long training, large data, RL, release MUST require exact canonical task authority.
- **FR-053:** MSTR-000 MUST NOT authorize long training or production release.
- **FR-054:** Closeout MUST produce bounded MSTR-001 proposal with compute/data/environment cost and rights constraints.
- **FR-055:** Closeout MUST receive independent review/reconciliation and explicit founder acceptance.

## Key Entities

CandidateModel, RightsDecision, ModelArtifact, RuntimeBuild, HardwareProfile, InteractionContract, DistributionContract, TaskManifest, RunEvidence, BenchmarkManifest, ContextArm, EnvironmentTask, VerifierDefinition, ProvenanceRecord, DecisionRecord. See `data-model.md`.

## Assumptions

- MSTR-000 is qualification, not long training.
- Python qualification harness is acceptable though eventual end-user runtime should favor self-contained portability.
- Final backbone/runtime/quant/context decisions are intentionally empirical.
- Upstream model/license/runtime facts must be revalidated at execution time.

## Success Criteria

- **SC-001:** package has zero unresolved `[NEEDS CLARIFICATION]` markers.
- **SC-002:** T000–T002 remain traceable canonical complete tasks.
- **SC-003:** every incomplete task has prerequisites, output path(s), and completion evidence.
- **SC-004:** at least three materially different eligible compact foundations survive static qualification or shortage is explicit.
- **SC-005:** each locally admitted candidate has pinned Q4/runtime identity.
- **SC-006:** required U1 results report 8K whole-laptop behavior without hidden discrete-GPU requirement.
- **SC-007:** rights/distribution/U1/artifact failures cannot win.
- **SC-008:** Interaction Contract v1 has deterministic fixture tests.
- **SC-009:** scorecards separate raw/neutral/full system.
- **SC-010:** final selection uses post-Q4/equivalent bounded-adaptation evidence.
- **SC-011:** context default is Pareto-efficient across solve rate/tokens/latency/RAM/disk/update.
- **SC-012:** environment MVP rejects no-op-pass and canonical reward shortcuts.
- **SC-013:** material results are fully traceable without chat history.
- **SC-014:** closeout package lets a new implementation agent proceed without redesign.
- **SC-015:** long training remains blocked until closeout/founder acceptance.
