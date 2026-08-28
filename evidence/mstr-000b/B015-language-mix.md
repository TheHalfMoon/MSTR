# B015 — Programming Language and Tooling Target Policy

**Task:** `B015`
**State:** IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT
**Policy:** `MSTR-LANGUAGE-TARGET-POLICY-v0`
**Canonical main at entry:** `205df4be5f2e25bd28b697816eac3ea6ce361aed`
**Entry gate:** run `33166914253` / job `98834411321` / `eligible=true` / drift clean
**External effect:** `NO_EXTERNAL_EFFECT`

## Decision

B015 freezes the language/tooling dimension required by `MSTR-DATA-CONSTITUTION-v0`. It does **not** freeze one final universal training mixture. Stage manifests still choose exact weights from evidence, but they must preserve the replay floors below so a narrow SFT/RL or fashionable ecosystem does not silently erase core coding capability.

### Core programming tier

```text
TypeScript
Python
JavaScript
Java
C#
C
C++
```

These languages cover the dominant GitHub/web/backend/enterprise/native software surfaces while preserving the systems/native work explicitly present in the MSTR product and tokenizer/evaluation plan.

### Secondary programming tier

```text
Go
Rust
PHP
Kotlin
Swift
```

This tier preserves important cloud/infrastructure, systems/safety, deployed-web, JVM/Android, and Apple-platform work without giving every ecosystem equal capacity merely for breadth.

### Long-tail tier

Initial bounded targets are Ruby, Dart, Scala, Elixir, Zig, Lua, R, and Objective-C. They have no per-language replay minimum. Stage allocation requires product tasks, evaluation failures, repository distribution, developer/customer demand, or strategic platform evidence. Marketing completeness is explicitly not evidence.

### Mandatory tooling/config channels

```text
POSIX shell + Bash/Zsh
PowerShell
SQL
JSON / YAML / TOML
package/build manifests
Make / CMake / Ninja / Dockerfile
CI workflows
HCL / Terraform
```

PowerShell is explicit because Windows is a required MSTR platform family. Shell, SQL, build, CI, and configuration are software-building skills rather than peripheral long-tail syntax.

## Replay floors

All percentages below are measured inside the stage's declared `LANGUAGE_TOOLING_SLICE`; they are **capacity-preservation guardrails**, not market-share estimates and not a claim that the final mixture is globally optimal.

```text
CORE_PROGRAMMING_AGGREGATE_MIN = 55%
SECONDARY_PROGRAMMING_AGGREGATE_MIN = 15%
TOOLING_CONFIG_AGGREGATE_MIN = 15%
LONG_TAIL_AGGREGATE_MAX = 15%
```

Core per-language minima:

```text
TypeScript 8%
Python     8%
JavaScript 6%
Java       6%
C#         5%
C          4%
C++        4%
```

Secondary per-language minima:

```text
Go     3%
Rust   3%
PHP    2%
Kotlin 2%
Swift  2%
```

Tooling-group minima:

```text
shell             4%
SQL               3%
structured config 3%
build + CI        3%
infrastructure    2%
```

After floors are met, the remainder is stage-specific and evidence-selected. A stage cannot silently zero an admissible core/secondary language. Any floor reduction or long-tail-cap increase requires a canonical B015 amendment with exact rationale and impact analysis.

B015 does not own the software-role mixture. It therefore does not set CODE/FIM/TEST/DIFF percentages; those remain stage-specific under B014.

## Evidence basis

### Canonical repository evidence

- `spec.md` FR-023 requires the language/tooling mixture to follow intended product usage and evidence, not marketing breadth.
- `plan.md` and B007 already require representative coverage including Python, TypeScript/JavaScript, Rust, Go, Java, C/C++, SQL, shell, structured configuration, diffs, paths, stack traces, and tool JSON.
- `MSTR_DATA_CONSTITUTION.md` deliberately delegates canonical language tiers/weights to B015 and requires the policy to be bound before training admission.
- The MSTR product must remain useful across Windows, Linux, and macOS, so shell/build/config behavior is part of product coverage rather than an optional language tail.

### External ecosystem evidence — supporting, not sole authority

Observed 2026-08-28:

1. GitHub Octoverse 2025: https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/
   - TypeScript became GitHub's #1 language in August 2025, ahead of Python and JavaScript.
   - Java and C# were #4/#5; PHP, Shell, C++, HCL, and Go were also top-ten languages.
   - JavaScript + TypeScript together remained larger than Python on GitHub.
2. Stack Overflow Developer Survey 2025: https://survey.stackoverflow.co/2025/technology
   - Python adoption rose seven percentage points from 2024 to 2025.
   - Rust was the most admired language at 72%.
   - Python developers showed strong interest in Rust and Go for performance-oriented systems programming.
3. JetBrains State of Developer Ecosystem 2025: https://blog.jetbrains.com/research/2025/10/state-of-developer-ecosystem-2025/
   - Based on 24,534 developers across 194 countries.
   - TypeScript showed the strongest five-year real-world usage rise; Rust, Go, and Kotlin also gained share.
   - Stated next-language adoption was led by Go (11%) and Rust (10%), with Python (7%), Kotlin (6%), and TypeScript (6%) also prominent.

The external sources use different methodologies and are not converted into token percentages. B015 uses them to identify durable/high-value ecosystems, then applies MSTR's software-building mission and capacity constraints.

## Why the replay floors are normative guardrails

The public ecosystem sources do not justify exact training-token percentages. The numeric floors are therefore explicitly normative product guardrails: they preserve broad capability in a tiny model while leaving at least 15 percentage points of the language/tooling slice flexible after aggregate minima are met. They are not popularity-weighted estimates. Later evidence may raise allocations freely; reducing a floor requires a governed B015 amendment so capacity tradeoffs stay reviewable.

## Stage-manifest requirements

Every downstream material stage that carries a language/tooling slice must:

1. declare the accounting unit and denominator;
2. make all four bucket totals inspectable and sum allocated shares to 100%;
3. satisfy aggregate, per-language, and tooling-group replay floors;
4. preserve B014 provenance, rights, contamination, dedup, benchmark-exclusion, verifier-health, and private-data rules;
5. refresh the evidence before each material training stage and record any inability to satisfy a floor;
6. use a canonical B015 amendment for tier/floor changes rather than silently changing the policy.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PAID_COMPUTE = NONE
PAID_MODEL_API = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
```

This task freezes a policy only. It does not admit a corpus, execute a model, or authorize training.
