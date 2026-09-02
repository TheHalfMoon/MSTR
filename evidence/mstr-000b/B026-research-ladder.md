# B026 — Multi-Fidelity Research Ladder v0 Evidence

**Task:** `B026`
**Implementation PR:** #137
**Final implementation head:** `ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421`
**Canonical implementation merge:** `1aed67793fa14e6c9a7bbe4067ad521d16617b26`
**State:** COMPLETE_CANONICAL
**Canonical entry main:** `823cd7ec3b4c537876a0795d0f0f8d4bd75acd85`
**Entry proof:** post-B024-closeout run `33564300212` — SUCCESS

## Entry gate

```text
ENTRY_GATE_TASK = B026
ENTRY_GATE_CANONICAL_MAIN = 823cd7ec3b4c537876a0795d0f0f8d4bd75acd85
ENTRY_GATE_ELIGIBLE = true
TASK = B026
CANONICAL_MAIN = 823cd7ec3b4c537876a0795d0f0f8d4bd75acd85
TASK_DRIFT = clean
B022_STATE = COMPLETE_CANONICAL
B024_STATE = COMPLETE_CANONICAL
B025_STATE = COMPLETE_CANONICAL
B026_STATE = PENDING
B026_ELIGIBLE = true
EXTERNAL_AUTHORITY_REQUIRED = false
B027 = blocked on B026
B011 = blocked on repository-specific external authority
```

## Frozen contract/config candidate

```text
MATERIAL_RESULT_SCHEMA = mstr.material-result-identity.v0
RESEARCH_EXPERIMENT_SCHEMA = mstr.research-experiment.v2
LADDER_CONFIG = configs/research/mstr-research-ladder-v0.json
FIDELITY = L0_CONTRACT_SMOKE -> L1_CODE_PROXY -> L2_EXECUTABLE_REPO -> L3_DIRECTION_TO_DONE -> L4_Q4_UNIVERSAL_LAPTOP
PROMOTION_CRITERIA_PREDECLARED = true
SEQUENTIAL_PROMOTION_ONLY = true
EARLY_HARD_REJECT = required
OPAQUE_MATERIAL_RESULT = invalid
MISSING_REQUIRED_IDENTITY = invalid
FROZEN_EVALUATION_IDENTITY = required
```

Every material result carries the full `MaterialResultIdentity` surface from the canonical data model. Fields that genuinely do not apply remain present with explicit `N/A`; required task/verifier identities cannot be `N/A`. `mstr.research-experiment.v2` binds one frozen evaluation identity and one fidelity level, records predeclared budget and hard-gate results, and rejects `PROMOTE` when any represented hard gate is not `PASS`.

The ladder config declares promotion and hard-reject conditions for every L0-L4 level and permits only sequential promotion. Weak experiments must be discarded before expensive levels. L4 preserves release-relevant Q4 identity, universal-laptop gates, and the B028 `Q4PromotionRecord` dependency for material weight-changing parentage.

## Authority boundary

This B026 work freezes contracts and configuration only. It does not execute B027 or any research campaign and grants no new execution or training authority.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
RESEARCH_CAMPAIGN_EXECUTION = NONE
TEST_GENERATION_EXECUTION = NONE
VERIFIER_EXECUTION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
```

B027 remains a separate canonical task. Any external effect required by a later campaign must pass its own exact-main eligibility and already-canonical authority gates; B026 task eligibility never creates or widens such authority.

## Independent review findings and repair

Fresh independent CodeRabbit review comment `5508683112` reviewed exact implementation head `a2414b1bf58a5bce3a69ee965e74d8ac9d0ba7a8` and found three High issues:

1. explicit offline CLI validation did not dispatch either B026 schema version;
2. exact-or-`N/A` identity fields admitted ambiguous sentinel values and the material-artifact SHA field did not require SHA-256 shape;
3. predecessor promotion and declared-budget hard-reject semantics were prose-only rather than machine-enforced.

The repair adds explicit CLI dispatch/tests, concrete identity rejection, SHA-256 shape enforcement, an explicit `predecessor_promotion` binding, immediate-predecessor/same-campaign/frozen-evaluation/parent-result semantic validation, material-result count checks, and declared budget ceilings. The task ledger and task-gate canonical state remain unchanged while B026 is implementation-active.

No review finding is considered resolved merely by this text. Resolution requires a successful guarded repair build, fresh exact-head qualification, and a fresh independent review of the repaired head. The authority boundary below remains unchanged.


## Codex review reconciliation — exact old head

Codex review `PRR_kwDOUCYTYs8AAAABL1K_JQ` on historical head `a2414b1bf58a5bce3a69ee965e74d8ac9d0ba7a8` produced six actionable threads. The first repair at `45d9f9f0ded97ebd482c29d419d2ff41bd9e940a` addressed predecessor adjacency, declared-budget enforcement, and SHA-256 identity semantics. The later `08399fa64ed82f31feb5b5cff2f92420bde36308` candidate added exact gate coverage, an authority-reference shape, and training data/difficulty identity, but fresh exact-head review correctly found that predecessor and authority evidence were still self-attested.

The external-effect authority object is evidence about authority granted elsewhere. It is not an authority grant. B026 remains contract/configuration only.


## Fresh exact-head review findings on `08399fa64ed82f31feb5b5cff2f92420bde36308`

Codex review `PRR_kwDOUCYTYs8AAAABL2PpKg` produced five actionable findings on the exact qualified head:

1. L4 promotion did not require concrete Q4 artifact/quantizer/runtime/hardware identity or bind Q4 gate evidence to those identities.
2. `predecessor_promotion` remained self-attested instead of resolving an immutable predecessor experiment record.
3. `external_effect_authority` remained self-attested instead of resolving the canonical authority artifact and deriving scope/ceilings from it.
4. governed external-effect classes were not exhaustively declared, allowing local/zero-cost training evidence to remain unbound.
5. aggregate paid cost was not reconciled with the sum of per-result paid costs.

CodeRabbit run `2b1e0aeb-8ecf-449f-bb4e-3ca2faa33ac6` independently confirmed the predecessor/authority resolution gaps and also required this evidence record to stop describing unresolved gaps as closed.

This guarded candidate repair addresses those findings by deriving predecessor records from `artifacts/results/research/<governing_task_id>/registry/<experiment_id>.json`, deriving authority only from `artifacts/authorities/<authority_id>.json`, binding both files by SHA-256, requiring an explicit boolean declaration for every canonical governed effect class, reconciling per-result paid cost to the aggregate, and requiring concrete per-level material identity with strict L4 Q4 evidence binding. The experiment record carries no copied authority scopes or ceilings.

These findings are not considered resolved by implementation text. Resolution still requires successful guarded repair gates, fresh exact-head qualification, thread reconciliation, and a new independent exact-head review.

## Fresh exact-head CodeRabbit review findings on `87d31a1c6488c80d8c6e35a4aadaf84a42fa20ac`

CodeRabbit review `PRR_kwDOUCYTYs8AAAABL3Tj7A` / run `2914d85c-a8dd-4db3-8d5c-3aef880343e0` reviewed the exact qualified 17-file head and completed with status `53388944096`. It produced three actionable findings:

1. the contract text said only that no hard gate failed while the schema correctly required every required gate to be `PASS` for `PROMOTE`;
2. the canonical `ResearchExperimentRecordV2` reading-order block omitted four schema-required fields;
3. semantic validation could fail to reject concrete Q4 promotion evidence on a non-L4 `PROMOTE` record because of an `elif` fallthrough.

This candidate chooses the stricter existing promotion semantics: every required gate must be `PASS`; `NOT_APPLICABLE` remains legal only for non-`PROMOTE` records. It synchronizes the ladder text and schema description, fixes the canonical data-model block, makes the Q4 restriction explicit at every non-L4/non-promote boundary, preserves caller-selected `schema_dir` for recursively resolved predecessor validation, adds byte-identity coverage for both B026 schema pairs, and binds the explicit CLI negative-fixture test to `schema.instance_invalid`.

The review also noted that canonical authority ceilings must not be treated as indefinitely reusable execution budget. B026 performs per-record ceiling validation only and grants no execution authority; cumulative authority-consumption accounting remains a mandatory responsibility of any future separately authorized external-effect executor. No cumulative authority or execution right is created here.

The broad sentinel-schema deduplication and wholesale rewriting of every historical generic negative-test assertion were maintainability nitpicks, not correctness findings, and are not claimed as part of this bounded repair.

These exact-head findings are not considered resolved by this evidence text. Resolution still requires guarded publication, fresh exact-head qualification, review-thread reconciliation, and a new independent exact-head substantive review.

## Fresh exact-head Codex review findings on `633a8a4ed8717eeeee2c1c42d3045e5658d5fb25`

Codex review `PRR_kwDOUCYTYs8AAAABL3vKoQ` reviewed exact head `633a8a4ed8717eeeee2c1c42d3045e5658d5fb25` after qualification run `33646862191` and produced two P1 findings: Q4 promotion evidence was not resolved to an immutable `mstr.q4-promotion.v0` record, and submitted hard-gate `PASS` values were not recomputed against a content-bound predeclared decision policy.

This bounded repair introduces no research execution. It freezes content-addressed registry semantics for predeclared promotion policies and gate-observation evidence, makes every gate evidence identity a lowercase `sha256:<digest>` of exact repository bytes, recomputes the submitted gate status from the predeclared criterion, and rejects missing/tampered/mismatched policy or evidence records. L4 now resolves the existing B028 `mstr.q4-promotion.v0` contract by content address, requires `PROMOTED`, binds the canonical Q4 artifact SHA-256 to the promoted material result, requires an actual universal-laptop `PASS`, and binds the Q4 record's laptop and promotion-decision evidence identities to the corresponding B026 hard gates.

The B026 repository records added under `artifacts/results/research/B026/` are contract fixtures for the existing valid schema fixture only. They are not a B027 campaign, model run, Q4 execution, training result, paid-compute result, or authority grant. No actual Q4 promotion artifact is added.

These findings are not considered resolved by prose. Resolution requires guarded publication, fresh exact-head qualification, explicit thread reconciliation, and a new independent exact-head review.

The `q4_artifact_identity` gate uses a predeclared symbolic criterion `EQ_PROMOTED_ARTIFACT`: its immutable gate-evidence record carries the observed artifact SHA-256, and validation compares that value to the selected promoted material result. This preserves content-addressed gate evidence without treating the gate-evidence identity itself as the model artifact identity.

## Exact-head review repair — canonical history and causal evidence

Codex review `PRR_kwDOUCYTYs8AAAABL4fRHw` on exact historical head `ffd526fd686c84572a023490c4ab69a3255b8780` identified six P1 defects: working-tree registry trust, missing model/network execution effects, missing pre-execution policy antecedence, self-declared gate observations, incomplete L4 universal-laptop enforcement, and missing Q4-to-candidate lineage binding.

This repair is contract/configuration hardening only. `CAMPAIGN_RESULT` now requires explicit Git commits in canonical-main ancestry: policy/predecessor/authority resolve from a strict ancestor campaign-freeze commit, while gate/verifier/Q4 evidence resolves from the later canonical evidence commit. Gate evidence derives observations from separately content-addressed verifier evidence instead of accepting an `observed_value` field in the gate record. Model execution and network model/teacher calls are explicit governed effects. L4 enforces the 8 GiB / CPU / 8K / Q4 <= 3 GiB envelope and a content-addressed Q4 candidate/source-checkpoint binding. B026 contract fixtures are explicitly non-campaign and cannot claim promotion.

The repair does not grant or execute model inference, model-weight access, network model/teacher calls, paid APIs or compute, dataset ingestion, training, RL, or release. Fresh exact-head qualification and fresh independent review remain required after publication of the repaired candidate.

## Exact-head CodeRabbit review repair — network evidence and verifier derivation

Fresh independent CodeRabbit issue review comment `5514766559` reviewed exact head `d2950bb1f254beedbac64268347c735f21e500c9` against canonical base `823cd7ec3b4c537876a0795d0f0f8d4bd75acd85`, resolved tree `0817e9fc29c40557e46765b8db72d60cf74f9283`, and reported two High actionable findings:

1. positive `resource_cost.network_bytes_or_na` could be accepted with zero model/teacher call count, all governed effects false, and no authority binding;
2. `mstr.research-verifier-evidence.v0` still carried a self-authored observed value without content-addressed bindings to the verifier manifest, verifier-health record, subject material evidence, and underlying verifier execution result.

This bounded repair derives the network effect from both the call counter and positive network-byte evidence. Any positive network bytes require `NETWORK_MODEL_OR_TEACHER_CALL=true`; any true governed effect continues to require a separately canonical authority record resolved from the campaign-freeze commit. No authority artifact or task ledger state is changed.

The verifier-evidence wrapper no longer carries `observed_value`. It binds content-addressed canonical verifier-manifest, verifier-health, subject-evidence, and verifier-result records from the canonical evidence commit. Validation verifies every digest and cross-binding, requires the health record to be `HEALTHY`, requires subject material evidence to exactly equal a material result in the experiment, and computes the gate observation only from the resolved verifier result at `/observed_value`. Adversarial tests cover positive network bytes with no effect declaration, a missing underlying verifier result, and mismatched subject material evidence.

These findings are not considered resolved by this text or by a local patch. Resolution requires a successful guarded repair publication, fresh exact-head qualification, a fresh independent substantive review of the newly published head, zero unresolved actionable review findings, and the mandatory exact-head premerge gate.

The authority boundary remains unchanged: B026 grants no model execution, network model/teacher call, paid compute/API, model-weight access, dataset ingestion, training/RL, research-campaign execution, or production-release authority. B027 remains separate and B011 remains blocked on its separately required external authority.

## Fresh exact-head CodeRabbit review finding on `f0cee46975693b52fc5f7e38677116b94ca98420`

Fresh independent CodeRabbit issue review comment `5515461479` reviewed exact head `f0cee46975693b52fc5f7e38677116b94ca98420` against canonical base `823cd7ec3b4c537876a0795d0f0f8d4bd75acd85` and resolved tree `6537e40ac335a4598a82b082e2e863332de9f31d`. It found one High causal-ordering defect: a higher-level policy freeze could reference a predecessor registry record whose own canonical evidence commit was only on a sibling or later-merged canonical history path, so the predecessor `PROMOTE` outcome was not necessarily available when the higher-level policy froze.

This bounded repair makes predecessor evidence causality machine-enforced. For L1-L4 campaign records, the resolved predecessor's `canonical_evidence_commit_sha_or_na` must be a strict canonical-main ancestor of the current `campaign_freeze_commit_sha_or_na`. The ladder promotion policy records this antecedence rule explicitly. An adversarial merge-history test constructs a predecessor evidence commit on a sibling history path, makes the predecessor registry record visible at the current policy freeze, later merges both paths into canonical main, and proves validation rejects the causally unavailable predecessor outcome. The existing linear promoted-chain tests continue to prove valid sequential promotion.

No task ledger, task-gate state, or authority artifact is changed. This repair grants no model execution, network model/teacher calls, paid compute/API, model-weight access, dataset ingestion, verifier execution, training/RL, research-campaign execution, Q4 execution, or production-release authority. The finding is not considered resolved by prose or a local patch; guarded publication, fresh exact-head qualification, fresh independent substantive review, zero unresolved actionable findings, and mandatory premerge verification remain required.

## Canonical Implementation Closeout

The B026 Multi-Fidelity MSTR Research Ladder v0 contract/configuration implementation merged and was re-verified on canonical main. This closeout records terminal task/provenance state only. It does not execute B027 and does not authorize model execution, model-weight access, verifier execution, teacher/API execution, paid compute/API, network model/teacher calls, data ingestion, training/RL, Q4 execution, or production release.

- implementation PR: `#137`
- final implementation head: `ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421`
- canonical implementation merge: `1aed67793fa14e6c9a7bbe4067ad521d16617b26`
- guarded final causal-ordering repair builder: run `33677458758` — SUCCESS
- exact-head qualification: run `33678090319` — SUCCESS
- exact-head independent review: CodeRabbit comment `5516237548` — NO ACTIONABLE COMMENTS on exact base/head/tree, 9 commits, and all 17 changed files
- mandatory exact-head pre-merge verification: run `33682188378` — SUCCESS
- post-merge implementation verification: run `33683456723` — SUCCESS

The final implementation review confirms canonical Git-blob resolution, strict campaign-freeze/evidence ordering, predecessor-evidence causality, verifier-evidence derivation, governed-effect authority binding, positive-network-byte effect derivation, and L4/Q4 identity controls. Earlier-head findings remain historical and are not represented as current findings.

This closeout changes only B026 canonical state/provenance, the canonical task ledger, and closeout regression coverage. The frozen B026 schemas, semantic validator, ladder configuration, and source implementation are unchanged by this closeout. B027 becomes machine-eligible only because B026 is now canonically complete. B011 remains separately blocked on repository-specific external authority.
