# B023 Cross-Workstream Prerequisite Binding Reconciliation

**State:** `IMPLEMENTATION_ACTIVE`

## Purpose

Reconcile the machine task gate with already-canonical MSTR-000A prerequisites A006 and A014 without granting B023 implementation authority by assertion. The repair remains repository-local, read-only, and fail-closed.

## Canonical diagnostic

On exact canonical `main=db12d1467bb81185a9affffb4d470626ceceddfa`, diagnostic run `33499263750` observed `task drift = clean` and `B023 eligible=false` because A006 and A014 returned `prerequisite.missing_task_binding`. B002 and B022 were independently recognized as `COMPLETE_CANONICAL`.

## Binding rule

An external prerequisite is satisfied only when the catalog contains an explicit repository-local cross-workstream binding, the exact bound canonical task checklist contains one checked task entry, the exact bound evidence declares both the expected task identity and `COMPLETE_CANONICAL`, and every required evidence path exists inside the repository. Unknown external prerequisite ids remain fail-closed.

## Authority boundary

This maintenance repair creates no external authority, candidate-pool decision, task completion state, model access, model execution, paid compute, training, large dataset ingestion, or production release. It only permits the existing B002 machine gate to verify already-canonical cross-workstream prerequisites.

## Independent-review hardening

The review repair binds each external prerequisite to an explicit fully qualified `task_identity`, permits only the repository-owned MSTR-000A checklist/evidence namespace for these v0 external bindings, and requires exactly one structured `Task` declaration plus exactly one structured `State` declaration in the bound canonical evidence. Duplicate or split identity/state records fail closed.

A006's older canonical evidence uses the legacy bare `A006` task token. The gate qualifies that token only through the explicit `MSTR-000A / A006` binding plus the enforced MSTR-000A checklist and evidence namespace; a bare token cannot select another workstream or evidence namespace. A014 already declares the fully qualified identity directly.

## Review diagnostic hardening

Independent review also identified that an absent, unreadable, or non-unique external checklist entry was reported as `prerequisite.state_checkbox_conflict`. The repair now distinguishes an unverifiable checklist as `prerequisite.external_checkbox_unverifiable` while preserving `prerequisite.state_checkbox_conflict` for a uniquely located but unchecked checklist entry. Both cases remain fail-closed.


## Final parser hardening from independent review

Independent review of the qualified candidate identified two additional fail-closed robustness defects. External checklist parsing no longer depends on an undocumented trailing period in task-title prose; it binds the exact task id and any non-empty bold task title instead. External checklist and state-evidence reads now treat invalid UTF-8 as unverifiable evidence rather than allowing `UnicodeDecodeError` to abort eligibility evaluation. Dedicated contract tests cover period-free checklist titles and malformed UTF-8 in both bound external artifact classes.

## Fenced Markdown hardening from independent review

Independent review of PR #127 identified that line-oriented external prerequisite parsing could treat declarations inside fenced Markdown examples as canonical evidence. The parser now removes backtick- and tilde-fenced code blocks before interpreting external checklist rows or structured `Task`/`State` declarations. Unclosed fences exclude the remaining fenced content, preserving fail-closed behavior. Regression tests prove fenced-only checklist/evidence examples cannot satisfy a prerequisite and that examples inside fences do not create duplicate/conflicting records when one canonical declaration exists outside the fence.


## Emphasized duplicate-row hardening from independent review

Independent exact-head review of PR #128 found that the external checklist matcher excluded task-title rows containing Markdown emphasis because the title character class rejected `*`. A checked canonical row plus an emphasized duplicate could therefore be misread as uniquely located. The matcher now accepts the full non-newline title payload after the exact task id, so every matching task row is counted and any duplicate remains fail-closed as `prerequisite.external_checkbox_unverifiable`. A dedicated regression covers a checked row plus an emphasized duplicate. The same review also identified and removed one redundant duplicate assertion in the fenced-state-evidence regression; that cleanup does not alter eligibility semantics.


## Regular-file evidence-output hardening from independent review

Independent exact-head review of PR #129 found that external `evidence_outputs` reused the generic repository-path presence helper, which accepts an existing directory as present. An external prerequisite could therefore list a repository-contained directory as an additional evidence output and still satisfy the evidence-presence check. External prerequisite evidence outputs now use a dedicated verifier that requires every literal output to resolve to a repository-contained regular file and requires glob patterns to match at least one repository-contained regular file. The generic task-output presence helper is intentionally unchanged because non-external task contracts may have different output-shape semantics. Dedicated regressions cover both a literal directory and a glob that matches only a directory; both remain fail-closed with `prerequisite.required_artifact_missing`.


## Horizontal-whitespace parser hardening from independent review

Independent exact-head review of PR #130 found two fail-closed parser defects. First, the fenced-Markdown parser used a raw regex character class containing `\\t`, which matches a literal backslash or `t` instead of an actual tab; a literal `t``` marker could therefore start a false fence and suppress later duplicate or conflicting canonical records. Fence indentation now recognizes only spaces and actual tab escapes. Second, structured `Task` and `State` declarations used `\s*`, allowing malformed newline-split declarations to be interpreted as canonical records. Their optional whitespace is now horizontal-only and captured values are constrained to one line. The same horizontal-only rule is applied proactively to external checklist whitespace so a task id and title cannot be joined across a newline. Regressions cover literal `t``` markers, real tab-indented fences, newline-split checklist rows, and newline-split `Task` and `State` declarations. All malformed forms remain fail-closed.
