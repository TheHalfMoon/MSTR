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
-> explicit weight gate if needed
-> ephemeral acquire
-> Q4/runtime/resource qualification
-> stable candidate pool
```

### Lane D — Data/training-signal foundation

Contracts and small fixtures may proceed without large corpus ingestion:

```text
Data Constitution
-> SoftwareEvolutionRecord
-> self-alignment/teacher contracts
-> difficulty/frontier contract
-> verifier-health contract
-> test-generation curriculum
-> greenfield/feature synthesis contract
-> Q4 regression contract
-> method-tournament preflight
```

### Convergence lane

Only after candidate and harness prerequisites:

```text
stable candidate pool
+ A001-A018 qualified loop/trajectory foundation
+ data/verifier/curriculum contracts
-> A019 cross-harness tournament
-> multi-fidelity research campaign
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
  external_effect_class
  required_authority_id?
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
- canonical state/task mismatch;
- candidate-pool stability requirement;
- current main identity.

This gate is advisory-enforced by tooling first and SHOULD later become a required repository check before autonomous task execution/merge.

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
- license/terms;
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
-> student generates task
-> student generates N solution/test candidates
-> execute in admitted sandbox
-> independent verifier health check
-> contamination/provenance check
-> difficulty calibration
-> admission decision
```

### Teacher rescue path

Triggered only for useful frontier tasks the student cannot solve reliably.

```text
frontier task
-> permitted teacher candidate(s)
-> N solutions
-> independent execution/verifier
-> rights/provenance
-> student-relative difficulty label
-> admission
```

Teacher identity and cost must remain explicit. Paid/API teachers require exact authority.

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

Training admission consumes verifier health, not only terminal test exit code.

## 11. Test Generation Curriculum

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

Each experiment has predeclared promotion criteria. An experiment may be discarded early for regression/hard-gate failure.

## 14. Training Method Preflight

Equivalent method cells use the same:
- base revision;
- dataset manifest;
- update/token budget;
- seed policy;
- context;
- eval checkpoints;
- export/Q4 path.

Candidate arms where supported:
- LoRA 16-bit;
- LoRA 16-bit + rsLoRA;
- QLoRA 4-bit;
- QLoRA 4-bit + rsLoRA.

The first smoke may use smaller samples. Full fine-tuning is outside default scope.

## 15. Q4-in-the-Loop

After a material checkpoint:

```text
checkpoint
-> merge/export
-> canonical Q4
-> integrity hash
-> L1 regression
-> selected L2/L3 regression
-> L4 when stage is a promotion/final decision
```

Q4 regressions can block promotion even if master-checkpoint metrics improve.

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

A001/A002 are already merged on live main at plan-authoring time. A003 is in PR #38. MSTR-000B does not reopen those implementations.

The old blanket MSTR-000A entry gate will be replaced with:

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
- treats harness gain as raw model gain.

**Result:** PASS_FOR_TASKING.
