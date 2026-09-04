# Plan — MSTR-000B Code Model Supremacy Foundation

**Status:** READY_FOR_CONSISTENCY_REVIEW  
**Workstream:** MSTR-000B  
**Weight-changing authority:** NONE

## 1. Constitution Check — Before Design

| Principle | Plan response |
|---|---|
| Universal laptop | All decisions preserve 8GB / CPU / 8K / Q4<=3GB primary product. |
| Local/private | No cloud inference dependency; private user repos not training data by default. |
| Evidence before selection | Mission-aligned rescan and equivalent candidate cells precede selection. |
| Rights/provenance | Candidate/data/teacher/tool rights fail closed independently. |
| Freeze coupled contracts | MSTR-000A loop/event/state/verifier contracts are prerequisites to material agent training. |
| TTVC/verified utility | DVCR + TTVC remain primary; capability/GB and repository-health metrics added. |
| Smallest sufficient architecture | One builder + deterministic verifier remains default. |
| Evaluation integrity | Verifier health, reward-shortcut testing, private/fresh tasks, contamination controls required. |
| Reproducibility/failures | Exact manifests; failed/invalid experiments preserved. |
| Bounded authority | New weight access/training/paid compute remain explicit founder gates. |

**Result:** PASS_FOR_PLANNING. No constitution amendment is required.

## 2. Execution Model

MSTR-000B is deliberately split into three lanes so planning work can advance without violating candidate/training gates.

### Lane G — Governance and sequencing

Immediate, model-independent:
- machine task graph;
- task eligibility validator;
- canonical drift detector;
- reconciliation of early-safe vs convergence MSTR-000A tasks.

### Lane B — Backbone and deployment economics

Metadata/static work can begin immediately. Artifact work waits for exact weight authority when outside T027/T028.

```text
rescan
-> static rights/provenance
-> tokenizer economics protocol
-> trainability/runtime/quantizer compatibility
-> bounded admission
-> explicit weight gate only if new access is required
-> ephemeral acquire when authorized
-> Q4/runtime/resource qualification for every qualification candidate
-> stable candidate pool
```

No-new-access is not the same as no-new-candidate: an already-authorized/already-available candidate still requires equivalent B012 qualification before B013.

### Lane D — Data/training-signal foundation

Contracts and small fixtures may proceed without large corpus ingestion as parallel branches from the Data Constitution:

```text
                         +-> language/tooling policy
Data Constitution -------+-> SoftwareEvolutionRecord -> fixture extractor
                         +-> self-alignment -> teacher-rescue policy
                         +-> difficulty -> frontier calibrator
                         +-> verifier-health contract -> evaluator -> test curriculum
                         +-> greenfield/feature curriculum
```

Q4 promotion and training-method preflight consume the relevant backbone/data/verifier contracts but grant no training authority.

### Convergence lane

Only after candidate and harness prerequisites:

```text
stable candidate pool
+ A001-A018 qualified loop/trajectory foundation
+ data/verifier/curriculum contracts
+ multi-fidelity research ladder
-> A019 cross-harness tournament
-> A020 bounded research campaign
-> downstream task supersession/reconciliation
-> explicit founder training gate
```

## 3. Machine Task-Gate Architecture

### Source of truth

Create a machine-readable task graph generated/maintained from canonical workstream task metadata.

Proposed runtime records:

```text
TaskNode
  task_id
  workstream
  state
  prerequisites[]
  output_paths[]
  evidence_outputs[]
  external_effect_class
  required_authority_id?
  candidate_pool_requirement_id?
  supersedes[]
  superseded_by[]
  parallel_safe
  candidate_dependent
```

### Validator

Add an offline command conceptually equivalent to:

```text
python -m mstr_qualify task eligible <TASK_ID>
```

It returns a structured result and non-zero exit when ineligible.

Checks:
- canonical predecessor completion;
- evidence/output existence where machine-verifiable;
- supersession;
- external authority binding;
- candidate-pool requirement binding;
- canonical state/task mismatch;
- current main identity.

### Bootstrap and mandatory enforcement

B001 and B002 are the only bootstrap exception because the validator cannot validate its own pre-existence. They use manual exact-prerequisite verification plus ordinary exact-head governance.

Once B002 is `COMPLETE_CANONICAL`, a successful validator result against exact current `main` is a **mandatory fail-closed prerequisite before every material B003+ task execution and again before merge**. Any `eligible=false`, validator error, unresolved predecessor, supersession, missing authority, candidate-pool mismatch, or canonical-state drift blocks execution/merge. This is not advisory and is not deferred to a later repository phase.

Authority semantics are explicit in the TaskNode contract. Candidate dependence never creates external-effect authority; gated external-effect classes require non-null exact authority, while candidate-dependent tasks require a canonical candidate-pool requirement identity.

## 4. Backbone Rescan Method

### Discovery classes

Do not search only general bases. Search:
- code-specialized base/foundation;
- general compact foundations;
- code-oriented controls;
- reference-only restricted/high-cost models.

### Initial mandatory review set

At minimum review live current status of:
- JetBrains/Mellum-4b-base;
- existing eight T022 candidates;
- compact CodeGemma base/code variants where product rights fit;
- StarCoder2 compact variants as rights-compatible primary/control/reference evidence permits;
- Stable Code compact variants as reference-only if rights remain incompatible;
- newly released compact code bases discovered during the rescan.

The list is discovery input, not admission.

### Candidate scorecard

Create normalized fields:

```text
rights_fit
base_provenance
params
context
source_bytes
q4_bytes
runtime_support
conversion_support
trainability
code_prior_evidence
fim_support
tokenizer_code_density
raw_code_score
repo_proxy_score
q4_regression
u1_resource_fit
```

No scalar score alone selects a winner. Hard product/rights gates precede Pareto ranking.

## 5. Tokenizer Economics Protocol

Use a frozen representative corpus containing at minimum:
- Python;
- TypeScript/JavaScript;
- Rust;
- Go;
- Java;
- C/C++;
- SQL;
- shell;
- JSON/YAML/TOML;
- diffs;
- stack traces;
- paths/tool JSON.

Measure exact bytes/tokens and fragmentation distributions. Pin tokenizer revision.

Do not change tokenizer merely for efficiency unless training/export/runtime consequences are separately proven. Tokenizer migration is a high-coupling change.

## 6. Data Constitution Architecture

Freeze a manifest-level target distribution rather than hard-code one final mixture prematurely.

Every data unit records:
- source/provenance;
- license/terms/rights decision;
- repository/revision identity;
- software role;
- language/tooling;
- synthetic/teacher/student origin;
- difficulty identity;
- contamination status;
- dedup lineage;
- benchmark exclusion state;
- verifier-health state;
- training-stage eligibility.

### Software-role taxonomy

```text
CODE
FIM
TEST
DIFF
BUILD_CI
TOOL_SHELL
ISSUE_DIRECTION
PR_REVIEW
SOFTWARE_EVOLUTION
REPAIR_RECOVERY
FEATURE_GREENFIELD
SECURITY
GENERAL_REASONING_REPLAY
```

The final mix is chosen by evidence and may vary across MSTR-001/002/003.

## 7. Software Evolution Pipeline

### Extraction

From legally admissible repositories:

```text
base commit
-> issue/PR direction
-> commit sequence
-> tests/CI events where available
-> review comments where admissible
-> repair sequence
-> merge/final revision
```

### Leakage barrier

When creating a step-level example, information from future steps/final patches MUST NOT enter model-visible input unless that example explicitly trains retrospective review.

### Derived training units

- localization;
- change planning;
- patch prediction;
- review response;
- CI-failure repair;
- rollback/recovery;
- stop/finalization.

## 8. Self-Alignment Factory

### Student path

```text
seed concept/repo slice
-> bind seed provenance + rights
-> student generates task
-> student generates N solution/test candidates
-> bind provenance + rights for every generated artifact
-> execute in admitted sandbox
-> independent verifier health check
-> contamination check
-> difficulty calibration
-> fail-closed admission decision
```

### Teacher rescue path

Triggered only for useful frontier tasks the student cannot solve reliably.

```text
frontier task
-> permitted teacher candidate(s)
-> N outputs
-> bind concrete output provenance + rights + contamination status
-> independent execution/verifier
-> student-relative difficulty label
-> admission or rejection
```

Teacher identity/terms alone do not prove output rights. Paid/API teachers require exact authority.

## 9. Student-Frontier Curriculum

Difficulty is checkpoint-relative.

### Calibration method

For a task or task family:
- run bounded samples under frozen harness/sampling;
- estimate solve probability and failure classes;
- combine with structural difficulty descriptors;
- classify into frontier buckets;
- refresh after meaningful model checkpoints.

### Sampling policy

Favor tasks near the learnable frontier while retaining:
- easier replay for stability;
- harder frontier for expansion;
- regression anchors;
- core FIM/direct-code replay.

No single difficulty threshold is frozen before pilot evidence.

## 10. Verifier Health Architecture

A verifier package contains:
- evaluator identity/hash;
- protected paths;
- oracle/reference behavior where available;
- no-op fail proof;
- mutation/shortcut results;
- coverage/type/build signals;
- generated-test independence notes;
- disagreement state.

Training admission consumes verifier health, not only terminal test exit code. B023 is blocked until exact A006 and A014 verifier foundations are canonical.

## 11. Test Generation Curriculum

Every admitted test-generation example binds provenance, rights, contamination, verifier health, and protected-path integrity.

Training examples should teach:

```text
understand expected behavior
-> create minimal reproduction
-> prove current failure
-> implement
-> run targeted tests
-> expand verification when risk justifies it
```

Negative examples include:
- tests that only match hardcoded output;
- weakening/deleting tests;
- modifying protected evaluator files;
- tests that pass both before and after a supposed fix without proving behavior.

## 12. Greenfield and Feature Curriculum

Maintain task difficulty bands:

```text
G0 function/utility
G1 module + tests
G2 file/component
G3 multi-file feature
G4 bounded service/CLI/library
G5 repeated feature evolution
```

Public evaluation may use FEA-Bench/ProgramBench-style protocols. Training data admission depends on source rights and contamination, not benchmark availability.

## 13. Multi-Fidelity Research Ladder

### L0
Contract/schema/unit smoke. Seconds/minutes.

### L1
Direct code, FIM, edit, tokenizer, tool-schema proxies. Cheap.

### L2
Executable small-repository tasks. Moderate.

### L3
Direction-to-Done feature/greenfield/recovery tasks. Expensive.

### L4
Canonical Q4 on universal-laptop hardware lanes. Most product-specific.

Each experiment has predeclared promotion criteria. An experiment may be discarded early for regression/hard-gate failure. Every material result serializes the exact `MaterialResultIdentity`; opaque result blobs cannot satisfy comparison evidence.

## 14. Training Method Preflight

Equivalent method cells use the same:
- base revision;
- dataset manifest;
- update/token budget;
- seed policy;
- context;
- eval checkpoints;
- export/Q4 path.

Every technically supported arm from the following set MUST be included:
- LoRA 16-bit;
- LoRA 16-bit + rsLoRA;
- QLoRA 4-bit;
- QLoRA 4-bit + rsLoRA.

Every unsupported arm must record the exact compatibility reason and evidence identity. The first smoke may use smaller samples. Full fine-tuning is outside default scope.

## 15. Q4-in-the-Loop

After every material weight-changing checkpoint:

```text
source checkpoint
-> merge/export
-> verify merged-master SHA-256
-> record export tool revision + recipe hash
-> canonical Q4
-> verify Q4 SHA-256
-> record quantizer revision + recipe hash
-> L1 regression
-> selected L2/L3 regression
-> L4/universal-laptop gate when required
-> Q4PromotionRecord
```

Promotion is fail closed. `Q4PromotionRecord=PROMOTED` requires complete immutable artifact/tool/recipe identity plus every required regression/integrity gate. Only a promoted checkpoint may become the parent of another material weight-changing stage. Master-checkpoint improvement alone cannot bypass this rule.

## 16. Repository Health Delta

Define language-aware measurements and a normalized reporting surface rather than one universal magic number.

Potential dimensions:
- duplicated code;
- dead/unused code;
- lint/type findings;
- cyclomatic/structural complexity;
- dependency count/growth;
- test failures/flakiness;
- architecture boundary violations;
- diff churn/rework.

Compare before/after multi-round Direction-to-Done sequences under fixed task order.

## 17. Cross-Harness Robustness

The same checkpoint is evaluated across:
- raw model where meaningful;
- H0 neutral minimal;
- H1 MSTR native;
- H2 WePLD.

A checkpoint that only works in one highly specific scaffold is flagged. Training may vary presentation forms while preserving semantic contracts to reduce brittle scaffold memorization.

## 18. Integration With Existing Work

### MSTR-000A

A001/A002/A003 are canonical. A004 is the next early-safe model-independent implementation candidate subject to exact prerequisites. MSTR-000B does not reopen those implementations.

The old blanket MSTR-000A entry gate is replaced with:

```text
EARLY_SAFE = A001-A018 where exact dependencies and no candidate result are required
CONVERGENCE = A019-A024 requires stable/equivalent candidate qualification + MSTR-000B prerequisites
```

### MSTR-000

T030-T034 remain responsible for existing-candidate local/Q4/runtime qualification. New candidates receive equivalent qualification through MSTR-000B tasks before joining any headline tournament.

### MSTR-001

Consumes Data Constitution, software-evolution, FIM, difficulty, Q4-loop and language-mix contracts.

### MSTR-002

Consumes self-alignment, test-generation, failure/recovery, minimality, same-loop trajectory and verifier-health contracts.

### MSTR-003

Consumes dynamic frontier curriculum, admitted executable environments, verifier-health/reward-shortcut controls and multi-fidelity experiment policy.

## 19. Constitution Check — After Design

No design element:
- raises the laptop floor;
- authorizes cloud serving;
- admits incompatible rights;
- allows hidden telemetry;
- permits evaluation mutation during research;
- starts weight-changing training;
- treats harness gain as raw model gain;
- allows an ineligible post-B002 B-task to execute/merge;
- allows a non-Q4-qualified material checkpoint to parent the next material stage.

**Result:** PASS_FOR_TASKING.

## 20. Frontier Acceleration Amendment — 2026-09-04

This section consumes `docs/canonical/MSTR_FRONTIER_ACCELERATION_STRATEGY.md` and `research-frontier-2026-09-04.md` when those files are canonical. It changes planning obligations only and creates no external-effect authority.

### 20.1 Why a freshness gate is required

B005-B010 are historical canonical work. They must not be rewritten merely because the external model frontier changes. However B013 is a future decision that claims the product-aligned candidate pool is stable. That claim is invalid if a material post-scan challenger is silently omitted.

Therefore B013 must bind an exact frontier snapshot before `stable_pool=true`.

```text
B012 complete
-> exact B013 entry
-> snapshot last canonical scan/access cutoff
-> inspect material releases after cutoff
-> explicit per-release disposition
-> unresolved plausible universal-laptop challenger?
   |
   +-> NO -> compare qualified evidence -> stable pool may freeze
   |
   +-> YES -> B013 remains PENDING
              -> create separately governed refresh/task-graph amendment
              -> preserve old task history
              -> obtain new exact authority if weight access is required
              -> equivalent qualification or evidence-backed rejection
              -> resume B013
```

For the 2026-09-04 frontier, `K2 Horizon 3.7B` is a mandatory review input because its size/coding focus could plausibly affect the primary candidate decision. Naming it does not admit it or authorize access.

### 20.2 Frontier snapshot fields

The B013 planning surface should bind at minimum:

```text
frontier_snapshot_id
snapshot_time
canonical_main
last_backbone_scan_identity
last_access_envelope_identity
sources_checked[]
material_releases[]
release_dispositions[]
refresh_required
refresh_evidence[]
stable_pool
```

A missing materially relevant release disposition blocks `stable_pool=true`.

### 20.3 Checkpoint-lineage substrate comparison

When a finalist family exposes compatible base/intermediate/final checkpoints, downstream MSTR-001 planning should compare immutable checkpoint lineage under equal bounded adaptation/evaluation rather than assume the final post-trained checkpoint is the best MSTR parent.

Required comparability includes:

```text
same admitted data/update budget
same seed policy
same context
same evaluation identity
same export/Q4 path
exact checkpoint revision/hash
```

### 20.4 Q4 anchor and low-bit research

The existing Q4 promotion contract is not weakened.

```text
Q4 = MANDATORY QUALITY / PRODUCT ANCHOR
```

Future MSTR-004 research may compare:

```text
Q4
Q3
Q2
STRUCTURED_TERNARY / SHERRY_CLASS
```

Sub-Q4 is a challenger lane only. If a method requires QAT, sparse training, distillation, recovery training, or another weight change, it is governed by exact training authority and material checkpoint promotion.

### 20.5 Agent-RL acceleration requirements

When B032 becomes eligible it must carry the following into MSTR-003 planning:

```text
PRODUCTION_COMPATIBLE_EXECUTABLE_RL
DYNAMIC_SYNTHETIC_ENVIRONMENT_GENERATION
PREVIOUS_MSTR_BOOTSTRAP_WITH_INDEPENDENT_ADMISSION
TARGETED_TRAJECTORY_FEEDBACK_AS_MEASURED_ARM
REWARD_SHORTCUT_BATTERY
FUTURE_GIT_HISTORY_ISOLATION
PUBLIC_SOLUTION / NETWORK LEAKAGE CONTROL
```

No synthetic task/environment can certify itself.

### 20.6 Adaptive effort and TTVC

MSTR-004 should test same-model bounded effort modes:

```text
FAST
NORMAL
DEEP
```

Budgets may differ for retrieval, planning, reasoning, branching, repair, and verification. Selection is by joint DVCR/TTVC/whole-laptop evidence, not raw tokens/second.

### 20.7 Sealed headline evaluation

MSTR-006 must distinguish:

```text
PUBLIC_CONTINUITY
SEALED_PUBLIC_DERIVED
FRESH_PRIVATE_MSTR_GAUNTLET
```

Headline evidence must control future Git history, public-solution/network access, evaluator/answer artifacts, and solution-bearing caches. Any discovered leakage invalidates or explicitly corrects the affected claim and remains negative evidence.

### 20.8 Constitution re-check after frontier amendment

The amendment:

- preserves the 8 GB / CPU / 8K / <=3 GB Q4 primary envelope;
- keeps Q4 mandatory;
- creates no model/weight/training/quantization/paid/release authority;
- prevents stale candidate selection rather than preselecting a new model;
- keeps one builder + independent deterministic verifier as default;
- strengthens evaluation-integrity requirements;
- keeps TTVC tied to verified success.

**Result:** PASS_FOR_TASKING / NO_CONSTITUTION_AMENDMENT_REQUIRED.