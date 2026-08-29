# MSTR Greenfield / Feature Curriculum v0

**Task:** `B025`
**Contract:** `mstr.greenfield-task.v0`
**Status:** implementation candidate — not canonical until governed merge and closeout

## Purpose

This curriculum prevents MSTR software evaluation and future training from collapsing into bug-patch-only work. It freezes a bounded Direction-to-Done progression for new functionality while preserving the MSTR Data Constitution, hidden-behavior integrity, verifier independence, universal-laptop constraints, and exact external-effect boundaries.

B025 is a contract-and-fixture task only. It does not generate real synthetic programs, execute a model, ingest a corpus, run a verifier-health classifier, acquire model weights, or authorize training.

## Complexity bands

| Band | Required shape | Representative scope |
|---|---|---|
| `G0_FUNCTION` | one bounded function or utility | pure transformation, parser helper, deterministic utility |
| `G1_MODULE_TESTS` | module plus tests | cohesive module/API with direct regression coverage |
| `G2_COMPONENT_FILE` | component or file-level behavior | CLI subcommand, adapter, component, config surface |
| `G3_MULTI_FILE_FEATURE` | coordinated multi-file feature | implementation + tests + config/docs where needed |
| `G4_BOUNDED_PROGRAM` | bounded service/CLI/library | self-contained local program with explicit resource budget |
| `G5_MULTI_ROUND_EVOLUTION` | at least two ordered feature-evolution steps | repeated changes with behavioral preservation across rounds |

The bands describe semantic and repository scope, not token count. Difficulty remains checkpoint-relative under B020/B021.

## Required task archetypes

A curriculum portfolio must materially cover:

```text
FEATURE_IMPLEMENTATION
GREENFIELD_PROGRAM
API_CLI_CONSTRUCTION
INTEGRATION
MIGRATION
BEHAVIOR_PRESERVING_REFACTOR
BUILD_CI_REPAIR
TEST_AUTHORING
BUG_REPAIR
```

`BUG_REPAIR` is retained but must not dominate the default product-evaluation mix. Stage-specific distribution manifests remain governed by `MSTR-DATA-CONSTITUTION-v0` and the B015 language/tooling policy.

## Manifest integrity

Every `mstr.greenfield-task.v0` record binds:

- exact task identity and one G0–G5 complexity band;
- a bounded natural-language direction;
- explicit task archetypes and allowed languages;
- exact environment identity and finite resource budget;
- hidden behavior manifest identity + SHA-256 with `hidden_from_model=true`;
- verifier manifest identity and required verifier-health class `HEALTHY`;
- contamination boundary evidence;
- source provenance and immutable source revision;
- concrete rights decision for MSTR training/evaluation use;
- generation method and, when synthetic, generator/verification evidence;
- admission class and deterministic rejection/diagnostic reasons.

No hidden behavior artifact may be model-visible. No unrestricted network policy exists in v0; executable tasks are `DISABLED` or `FIXTURE_ONLY` unless a later canonical contract explicitly changes the boundary.

## Data Constitution gate

`CURRICULUM_ELIGIBLE` is fail-closed. It requires:

```text
RIGHTS_DECISION = COMPATIBLE
BENCHMARK_OVERLAP = CLEAR
HIDDEN_ANSWER_EXPOSURE = CLEAR
FUTURE_HISTORY_EXPOSURE = CLEAR
CROSS_SPLIT_DUPLICATE = CLEAR
ADMISSION_REASONS = []
VERIFIER_HEALTH_REQUIREMENT = HEALTHY
```

The manifest records the requirement; B025 does not claim that B023 verifier-health execution exists. A downstream executable admission pipeline must bind actual verifier-health evidence before using a task as clean positive signal.

## Feature-tree and semantic synthesis

Feature-tree / semantic-complexity synthesis is an **experimental generator**, never an authority source.

```text
FEATURE_TREE_SYNTHESIS
SEMANTIC_SYNTHESIS
```

For either method:

1. `synthesis_evidence` is mandatory;
2. the generator identity and immutable revision are mandatory;
3. `proposal_only=true` is mandatory;
4. an unverified or rejected proposal cannot be `CURRICULUM_ELIGIBLE`;
5. `VERIFIED` requires an independent verifier identity and evidence identity;
6. independent verification does not bypass provenance, rights, contamination, hidden-behavior, Data Constitution, or later verifier-health gates.

Synthetic generation is therefore a task proposal mechanism. It is not self-certifying training data.

## G5 multi-round evolution

`G5_MULTI_ROUND_EVOLUTION` requires at least two unique ordered evolution-step identities. Earlier-step model-visible context must not contain later hidden behavior, later patches, future review outcomes, or final answers. The B016 future-history boundary remains authoritative.

## Evaluation posture

Public FEA-Bench/ProgramBench-style protocols may inform future evaluation design, but benchmark availability never grants training-data rights or contamination clearance. Repository-owned fixtures are sufficient for B025 contract qualification.

Metrics should ultimately preserve the program north stars:

```text
DVCR
TTVC
FPAR
ESR
RSR
TER
RHD
VC_PER_GB
```

Band-level reporting must keep raw task success separate from harness-only gains and from future checkpoint difficulty labels.

## Non-authorities

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
VERIFIER_HEALTH_EVALUATOR_EXECUTION = NONE
SYNTHESIS_EXECUTION = NONE
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

B025 freezes curriculum semantics only. It never converts a proposal, fixture, benchmark, or generator output into project authority.
