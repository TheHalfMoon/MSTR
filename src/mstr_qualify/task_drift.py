"""Read-only canonical task drift detection for MSTR-000B B003.

The detector compares repository-local machine task state, canonical task
checkboxes, machine-readable evidence metadata, and Git merge history. It never
mutates task state, creates authority, or performs network I/O. Authoritative
execution requires a clean checkout where HEAD, local main, and the already
refreshed origin/main identity agree.
"""

from __future__ import annotations

import glob
import re
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import QualificationError
from .task_gate import DEFAULT_TASK_CATALOG, TaskCatalog, load_task_catalog

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_TASK_HEADING_RE = re.compile(r"^- \[[ xX]\] \*\*(?P<task_id>B\d{3}) ")
_IMPLEMENTATION_RE = re.compile(
    r"Canonical implementation:\s*PR #(?P<pr>\d+)\s*/\s*"
    r"final head `(?P<head>[0-9a-f]{40})`\s*/\s*"
    r"merge `(?P<merge>[0-9a-f]{40})`"
)
_EVIDENCE_STATE_RE = re.compile(
    r"^\*\*State:\*\*\s*`?(?P<value>[A-Z][A-Z0-9_]*)`?\s*$",
    re.MULTILINE,
)
_EVIDENCE_PR_RE = re.compile(r"^\*\*Implementation PR:\*\*\s*`?#(?P<value>\d+)`?\s*$", re.MULTILINE)
_EVIDENCE_HEAD_RE = re.compile(
    r"^\*\*Final implementation head:\*\*\s*`(?P<value>[0-9a-f]{40})`\s*$",
    re.MULTILINE,
)
_EVIDENCE_MERGE_RE = re.compile(
    r"^\*\*Canonical implementation merge:\*\*\s*`(?P<value>[0-9a-f]{40})`\s*$",
    re.MULTILINE,
)
_ENTRY_GATE_TASK_RE = re.compile(r"^ENTRY_GATE_TASK\s*=\s*(?P<value>B\d{3})\s*$", re.MULTILINE)
_ENTRY_GATE_MAIN_RE = re.compile(
    r"^ENTRY_GATE_CANONICAL_MAIN\s*=\s*(?P<value>[0-9a-f]{40})\s*$",
    re.MULTILINE,
)
_ENTRY_GATE_ELIGIBLE_RE = re.compile(
    r"^ENTRY_GATE_ELIGIBLE\s*=\s*(?P<value>true|false)\s*$",
    re.MULTILINE,
)
_MERGE_SUBJECT_RES = (
    re.compile(r"^Merge pull request #(?P<pr>\d+)\b"),
    re.compile(r"^Merge PR #(?P<pr>\d+)\b"),
    re.compile(r"\(#(?P<pr>\d+)\)\s*$"),
)


@dataclass(frozen=True)
class ImplementationRecord:
    """Canonical task-markdown implementation identity."""

    pr_number: int
    final_head: str
    merge_sha: str


@dataclass(frozen=True)
class EvidenceMetadata:
    """Machine-readable metadata extracted from one evidence file."""

    path: str
    state: str | None
    implementation_pr: int | None
    final_head: str | None
    merge_sha: str | None
    entry_gate_task: str | None
    entry_gate_main: str | None
    entry_gate_eligible: bool | None


def _git(root: Path, *args: str, code: str = "task_drift.git") -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise QualificationError(
            "unable to inspect repository Git state for canonical drift",
            code=code,
            details={"root": str(root), "args": list(args)},
        ) from exc


def _git_identity(root: Path, ref: str, *, code: str) -> str:
    completed = _git(root, "rev-parse", "--verify", ref, code=code)
    value = completed.stdout.strip().lower()
    if completed.returncode != 0 or not _HEX40_RE.fullmatch(value):
        raise QualificationError(
            "required Git identity is unavailable or invalid",
            code=code,
            details={"ref": ref, "returncode": completed.returncode, "value": value},
        )
    return value


def _trusted_canonical_main(root: Path) -> str:
    head = _git_identity(root, "HEAD", code="task_drift.head_invalid")
    local_main = _git_identity(root, "refs/heads/main", code="task_drift.main_ref_invalid")
    origin_main = _git_identity(
        root,
        "refs/remotes/origin/main",
        code="task_drift.origin_main_ref_invalid",
    )
    if local_main != origin_main:
        raise QualificationError(
            "local main does not match the refreshed origin/main identity",
            code="task_drift.main_ref_mismatch",
            details={"main": local_main, "origin_main": origin_main},
        )
    if head != local_main:
        raise QualificationError(
            "canonical drift detection must execute at canonical main",
            code="task_drift.not_canonical_main",
            details={"head": head, "canonical_main": local_main},
        )
    status = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        code="task_drift.status",
    )
    if status.returncode != 0:
        raise QualificationError(
            "unable to verify clean checkout for canonical drift",
            code="task_drift.status",
            details={"returncode": status.returncode},
        )
    if status.stdout.strip():
        raise QualificationError(
            "canonical drift detection refuses a dirty checkout",
            code="task_drift.dirty_checkout",
            details={"entries": status.stdout.splitlines()},
        )
    return head


def _safe_existing_file(root: Path, candidate: Path) -> Path | None:
    resolved_root = root.resolve()
    try:
        relative = candidate.relative_to(resolved_root)
    except ValueError:
        return None
    cursor = resolved_root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return None
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def _evidence_files(root: Path, node: dict[str, Any]) -> tuple[Path, ...]:
    found: dict[str, Path] = {}
    for raw in node["evidence_outputs"]:
        if not isinstance(raw, str):
            continue
        candidate = root / raw
        raw_matches: Iterator[Path]
        if any(marker in raw for marker in ("*", "?", "[")):
            raw_matches = (Path(value) for value in glob.glob(str(candidate), recursive=True))
        else:
            raw_matches = iter((candidate,))
        for match in raw_matches:
            safe = _safe_existing_file(root, match)
            if safe is not None:
                found[safe.as_posix()] = safe
    return tuple(found[key] for key in sorted(found))


def _evidence_pattern_present(root: Path, raw: str) -> bool:
    candidate = root / raw
    if any(marker in raw for marker in ("*", "?", "[")):
        matches = (Path(value) for value in glob.glob(str(candidate), recursive=True))
        return any(_safe_existing_file(root, match) is not None for match in matches)
    return _safe_existing_file(root, candidate) is not None


def _match_text(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group("value") if match else None


def _parse_evidence(path: Path, root: Path) -> EvidenceMetadata:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise QualificationError(
            "canonical evidence is unreadable",
            code="task_drift.evidence_read",
            details={"path": str(path)},
        ) from exc
    pr_raw = _match_text(_EVIDENCE_PR_RE, text)
    eligible_raw = _match_text(_ENTRY_GATE_ELIGIBLE_RE, text)
    return EvidenceMetadata(
        path=path.relative_to(root).as_posix(),
        state=_match_text(_EVIDENCE_STATE_RE, text),
        implementation_pr=int(pr_raw) if pr_raw is not None else None,
        final_head=_match_text(_EVIDENCE_HEAD_RE, text),
        merge_sha=_match_text(_EVIDENCE_MERGE_RE, text),
        entry_gate_task=_match_text(_ENTRY_GATE_TASK_RE, text),
        entry_gate_main=_match_text(_ENTRY_GATE_MAIN_RE, text),
        entry_gate_eligible=(eligible_raw == "true") if eligible_raw is not None else None,
    )


def _parse_implementation_records(tasks_file: Path) -> dict[str, ImplementationRecord]:
    try:
        lines = tasks_file.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise QualificationError(
            "canonical task markdown is unreadable for drift detection",
            code="task_drift.tasks_read",
            details={"path": str(tasks_file)},
        ) from exc
    current: str | None = None
    records: dict[str, ImplementationRecord] = {}
    for line in lines:
        heading = _TASK_HEADING_RE.match(line)
        if heading:
            current = heading.group("task_id")
            continue
        if current is None:
            continue
        match = _IMPLEMENTATION_RE.search(line)
        if not match:
            continue
        if current in records:
            raise QualificationError(
                "canonical task markdown contains duplicate implementation records",
                code="task_drift.implementation_record_duplicate",
                details={"task_id": current},
            )
        records[current] = ImplementationRecord(
            pr_number=int(match.group("pr")),
            final_head=match.group("head"),
            merge_sha=match.group("merge"),
        )
    return records


def _pr_from_commit_subject(subject: str) -> int | None:
    for pattern in _MERGE_SUBJECT_RES:
        match = pattern.search(subject)
        if match is not None:
            return int(match.group("pr"))
    return None


def _merge_commits_by_pr(root: Path) -> dict[int, tuple[str, ...]]:
    completed = _git(root, "log", "HEAD", "--format=%H%x09%s", code="task_drift.log")
    if completed.returncode != 0:
        raise QualificationError(
            "unable to inspect canonical merge history",
            code="task_drift.log",
            details={"returncode": completed.returncode},
        )
    matches: dict[int, list[str]] = {}
    for line in completed.stdout.splitlines():
        if "\t" not in line:
            continue
        sha, subject = line.split("\t", 1)
        pr_number = _pr_from_commit_subject(subject)
        if pr_number is not None and _HEX40_RE.fullmatch(sha):
            matches.setdefault(pr_number, []).append(sha)
    return {key: tuple(value) for key, value in matches.items()}


def _commit_exists(root: Path, sha: str) -> bool:
    completed = _git(root, "cat-file", "-e", f"{sha}^{{commit}}", code="task_drift.commit")
    return completed.returncode == 0


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    completed = _git(
        root,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        code="task_drift.ancestry",
    )
    if completed.returncode not in (0, 1):
        raise QualificationError(
            "unable to evaluate canonical Git ancestry",
            code="task_drift.ancestry",
            details={
                "ancestor": ancestor,
                "descendant": descendant,
                "returncode": completed.returncode,
            },
        )
    return completed.returncode == 0


def _unique_value(
    task_id: str,
    field: str,
    values: set[Any],
    findings: list[dict[str, Any]],
) -> Any | None:
    if len(values) > 1:
        findings.append(
            {
                "task_id": task_id,
                "code": "evidence.metadata_conflict",
                "details": {"field": field, "values": sorted(str(value) for value in values)},
            }
        )
        return None
    return next(iter(values)) if values else None


def _task_number(task_id: str) -> int:
    return int(task_id[1:])


def _finding(task_id: str, code: str, **details: Any) -> dict[str, Any]:
    return {"task_id": task_id, "code": code, "details": details}


def _scan_task(
    root: Path,
    catalog: TaskCatalog,
    task_id: str,
    implementation: ImplementationRecord | None,
    merge_history: dict[int, tuple[str, ...]],
) -> list[dict[str, Any]]:
    node = catalog.nodes[task_id]
    checked = catalog.checked.get(task_id)
    terminal = node["canonical_state"] in node["closeout_rule"]["terminal_states"]
    findings: list[dict[str, Any]] = []

    if checked is None or checked is not terminal:
        findings.append(
            _finding(
                task_id,
                "state.checkbox_conflict",
                canonical_state=node["canonical_state"],
                checkbox=checked,
                terminal_states=node["closeout_rule"]["terminal_states"],
            )
        )

    if terminal and node["closeout_rule"]["require_all_evidence_outputs"]:
        missing_evidence = [
            raw for raw in node["evidence_outputs"] if not _evidence_pattern_present(root, raw)
        ]
        if missing_evidence:
            findings.append(
                _finding(
                    task_id,
                    "evidence.required_missing",
                    paths=missing_evidence,
                )
            )

    metadata = tuple(_parse_evidence(path, root) for path in _evidence_files(root, node))
    if terminal and node["closeout_rule"]["require_all_evidence_outputs"]:
        invalid_state_paths = sorted(
            entry.path for entry in metadata if entry.state != node["canonical_state"]
        )
        if invalid_state_paths:
            findings.append(
                _finding(
                    task_id,
                    "evidence.terminal_state_mismatch",
                    paths=invalid_state_paths,
                )
            )

    states = {entry.state for entry in metadata if entry.state is not None}
    prs = {entry.implementation_pr for entry in metadata if entry.implementation_pr is not None}
    heads = {entry.final_head for entry in metadata if entry.final_head is not None}
    merges = {entry.merge_sha for entry in metadata if entry.merge_sha is not None}
    gate_tasks = {entry.entry_gate_task for entry in metadata if entry.entry_gate_task is not None}
    gate_mains = {entry.entry_gate_main for entry in metadata if entry.entry_gate_main is not None}
    gate_eligible_values = {
        entry.entry_gate_eligible for entry in metadata if entry.entry_gate_eligible is not None
    }

    evidence_state = _unique_value(task_id, "state", states, findings)
    evidence_pr = _unique_value(task_id, "implementation_pr", prs, findings)
    evidence_head = _unique_value(task_id, "final_head", heads, findings)
    evidence_merge = _unique_value(task_id, "merge_sha", merges, findings)
    gate_task = _unique_value(task_id, "entry_gate_task", gate_tasks, findings)
    gate_main = _unique_value(task_id, "entry_gate_main", gate_mains, findings)
    gate_eligible = _unique_value(task_id, "entry_gate_eligible", gate_eligible_values, findings)

    if evidence_state in node["closeout_rule"]["terminal_states"] and not terminal:
        findings.append(
            _finding(
                task_id,
                "evidence.completion_claim_active_task",
                canonical_state=node["canonical_state"],
            )
        )
    if terminal and evidence_state != node["canonical_state"]:
        findings.append(
            _finding(
                task_id,
                "evidence.terminal_state_mismatch",
                canonical_state=node["canonical_state"],
                evidence_state=evidence_state,
            )
        )

    history_merges: tuple[str, ...] = ()
    if evidence_pr is not None:
        history_merges = merge_history.get(int(evidence_pr), ())
        if not history_merges:
            findings.append(
                _finding(
                    task_id,
                    "git.pr_merge_unverifiable",
                    pr_number=evidence_pr,
                )
            )
        if len(history_merges) > 1:
            findings.append(
                _finding(
                    task_id,
                    "git.pr_merge_ambiguous",
                    pr_number=evidence_pr,
                    merges=list(history_merges),
                )
            )
        if history_merges and not terminal:
            findings.append(
                _finding(
                    task_id,
                    "implementation.merged_while_active",
                    pr_number=evidence_pr,
                    merge_sha=history_merges[0],
                    canonical_state=node["canonical_state"],
                )
            )

    identity_values = {
        "implementation_pr": evidence_pr,
        "final_head": evidence_head,
        "merge_sha": evidence_merge,
    }
    identity_comparison_required = (
        (terminal and task_id not in {"B001", "B002"})
        or implementation is not None
        or bool(history_merges)
        or any(value is not None for value in identity_values.values())
    )
    if identity_comparison_required:
        missing_identity_fields = sorted(
            field for field, value in identity_values.items() if value is None
        )
        if missing_identity_fields:
            findings.append(
                _finding(
                    task_id,
                    "evidence.implementation_identity_missing",
                    missing_fields=missing_identity_fields,
                )
            )

    if implementation is not None:
        if not terminal:
            findings.append(
                _finding(
                    task_id,
                    "implementation.record_while_active",
                    pr_number=implementation.pr_number,
                    merge_sha=implementation.merge_sha,
                    canonical_state=node["canonical_state"],
                )
            )
        implementation_commits = (
            ("final_head", implementation.final_head),
            ("merge_sha", implementation.merge_sha),
        )
        for label, sha in implementation_commits:
            if not _commit_exists(root, sha):
                findings.append(
                    _finding(
                        task_id,
                        "git.implementation_commit_missing",
                        field=label,
                        sha=sha,
                    )
                )
        final_head_exists = _commit_exists(root, implementation.final_head)
        merge_sha_exists = _commit_exists(root, implementation.merge_sha)
        if final_head_exists and merge_sha_exists:
            if not _is_ancestor(root, implementation.final_head, implementation.merge_sha):
                findings.append(
                    _finding(
                        task_id,
                        "git.final_head_not_in_merge",
                        final_head=implementation.final_head,
                        merge_sha=implementation.merge_sha,
                    )
                )
            current_head = _git_identity(root, "HEAD", code="task_drift.head_invalid")
            if not _is_ancestor(root, implementation.merge_sha, current_head):
                findings.append(
                    _finding(task_id, "git.merge_not_on_main", merge_sha=implementation.merge_sha)
                )
        if evidence_pr is not None and int(evidence_pr) != implementation.pr_number:
            findings.append(
                _finding(
                    task_id,
                    "evidence.implementation_identity_mismatch",
                    field="pr_number",
                    evidence=evidence_pr,
                    task_record=implementation.pr_number,
                )
            )
        if evidence_head is not None and evidence_head != implementation.final_head:
            findings.append(
                _finding(
                    task_id,
                    "evidence.implementation_identity_mismatch",
                    field="final_head",
                    evidence=evidence_head,
                    task_record=implementation.final_head,
                )
            )
        if evidence_merge is not None and evidence_merge != implementation.merge_sha:
            findings.append(
                _finding(
                    task_id,
                    "evidence.implementation_identity_mismatch",
                    field="merge_sha",
                    evidence=evidence_merge,
                    task_record=implementation.merge_sha,
                )
            )
        if history_merges and implementation.merge_sha not in history_merges:
            findings.append(
                _finding(
                    task_id,
                    "git.pr_merge_record_mismatch",
                    pr_number=implementation.pr_number,
                    task_record_merge=implementation.merge_sha,
                    history_merges=list(history_merges),
                )
            )

    requires_entry_gate = _task_number(task_id) >= 3 and (
        implementation is not None or bool(history_merges) or terminal
    )
    if requires_entry_gate:
        if gate_task is None or gate_main is None or gate_eligible is None:
            findings.append(
                _finding(
                    task_id,
                    "entry_gate.evidence_missing",
                    entry_gate_task=gate_task,
                    entry_gate_main=gate_main,
                    entry_gate_eligible=gate_eligible,
                )
            )
        else:
            if gate_task != task_id:
                findings.append(
                    _finding(
                        task_id,
                        "entry_gate.task_mismatch",
                        observed=gate_task,
                        expected=task_id,
                    )
                )
            if gate_eligible is not True:
                findings.append(
                    _finding(task_id, "entry_gate.not_eligible", observed=gate_eligible)
                )
            if not _commit_exists(root, str(gate_main)):
                findings.append(_finding(task_id, "entry_gate.main_missing", sha=gate_main))
            comparison_head = (
                implementation.final_head if implementation is not None else evidence_head
            )
            if comparison_head is None and history_merges:
                findings.append(
                    _finding(
                        task_id,
                        "entry_gate.final_head_missing",
                        pr_number=evidence_pr,
                    )
                )
            elif (
                comparison_head is not None
                and _commit_exists(root, str(gate_main))
                and _commit_exists(root, comparison_head)
            ):
                if not _is_ancestor(root, str(gate_main), comparison_head):
                    findings.append(
                        _finding(
                            task_id,
                            "entry_gate.after_implementation",
                            entry_gate_main=gate_main,
                            final_head=comparison_head,
                        )
                    )

    return findings


def detect_canonical_drift(
    *,
    repository_root: Path | None = None,
    catalog_path: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic drift report for the verified canonical-main checkout."""

    root = (repository_root or _REPOSITORY_ROOT).resolve()
    canonical_main = _trusted_canonical_main(root)
    effective_catalog = catalog_path or (root / DEFAULT_TASK_CATALOG.relative_to(_REPOSITORY_ROOT))
    catalog = load_task_catalog(effective_catalog, repository_root=root)
    implementation_records = _parse_implementation_records(catalog.tasks_file)
    merge_history = _merge_commits_by_pr(root)

    findings: list[dict[str, Any]] = []
    for task_id in sorted(catalog.nodes):
        findings.extend(
            _scan_task(
                root,
                catalog,
                task_id,
                implementation_records.get(task_id),
                merge_history,
            )
        )
    findings.sort(key=lambda item: (str(item["task_id"]), str(item["code"]), repr(item["details"])))
    return {
        "status": "drift" if findings else "clean",
        "canonical_main": canonical_main,
        "tasks_checked": len(catalog.nodes),
        "findings": findings,
    }
