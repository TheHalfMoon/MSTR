"""Offline, fail-closed task eligibility evaluation for MSTR-000B B002.

The gate reads only repository-local canonical metadata. It never mutates task
state, creates authority, contacts a remote service, or infers permission from
an identifier alone. Normal CLI evaluation fails closed unless the checkout is
clean and HEAD matches an explicit canonical-main SHA supplied by the
execution/merge governance path. The validator never treats an unrefreshed local
branch or remote-tracking ref as proof of current canonical main.
"""

from __future__ import annotations

import glob
import hashlib
import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import QualificationError
from .schemas import validate_instance, validation_errors

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASK_CATALOG = _REPOSITORY_ROOT / "configs" / "task-gate" / "mstr-000b.json"

_TASK_LINE_RE = re.compile(
    r"^- \[(?P<mark>[ xX])\] \*\*(?P<task_id>B\d{3}) (?P<title>.+?)\.\*\*",
    re.MULTILINE,
)
_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_BINDING_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_TERMINAL_COMPLETE = {"COMPLETE_CANONICAL"}
_GATED_EFFECTS = {
    "MODEL_WEIGHT_ACCESS",
    "GATED_TERMS_ACCEPTANCE",
    "PAID_MODEL_API_EXECUTION",
    "PAID_COMPUTE",
    "RENTED_COMPUTE",
    "LARGE_DATASET_INGESTION",
    "WEIGHT_CHANGING_TRAINING",
    "LONG_TRAINING",
    "LARGE_SCALE_RL",
    "PRODUCTION_RELEASE",
}
_MISSING_AUTHORITY_SENTINEL = "MISSING_REQUIRED_AUTHORITY_ID"
_MISSING_POOL_SENTINEL = "MISSING_CANDIDATE_POOL_REQUIREMENT_ID"


@dataclass(frozen=True)
class TaskCatalog:
    """Validated repository-local task catalog plus independent checkbox truth."""

    repository_root: Path
    tasks_file: Path
    nodes: dict[str, dict[str, Any]]
    checked: dict[str, bool]
    unresolved_bindings: dict[str, str]
    external_prerequisites: dict[str, dict[str, Any]]


def _read_json_object(path: Path, *, code: str) -> dict[str, Any]:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise QualificationError(
            "unable to read task-gate JSON",
            code=f"{code}.read",
            details={"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise QualificationError(
            "task-gate JSON is invalid",
            code=f"{code}.json",
            details={"path": str(path), "line": exc.lineno, "column": exc.colno},
        ) from exc
    if not isinstance(decoded, dict):
        raise QualificationError(
            "task-gate JSON root must be an object",
            code=f"{code}.root_type",
            details={"path": str(path)},
        )
    return decoded


def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key, value in base.items():
        merged[key] = dict(value) if isinstance(value, dict) else value
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(dict(merged[key]), value)
        else:
            merged[key] = value
    return merged


def _repository_path(root: Path, raw: str, *, field: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute() or "\\" in raw or ":" in raw or ".." in candidate.parts:
        raise QualificationError(
            "task-gate path must be repository-relative POSIX-style",
            code="task_gate.path_invalid",
            details={"field": field, "value": raw},
        )
    return root / candidate


def _parse_task_markdown(path: Path) -> tuple[dict[str, str], dict[str, bool]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise QualificationError(
            "canonical task markdown is unreadable",
            code="task_gate.tasks_read",
            details={"path": str(path)},
        ) from exc
    titles: dict[str, str] = {}
    checked: dict[str, bool] = {}
    for match in _TASK_LINE_RE.finditer(text):
        task_id = match.group("task_id")
        if task_id in titles:
            raise QualificationError(
                "canonical task markdown contains duplicate task identity",
                code="task_gate.task_duplicate",
                details={"task_id": task_id, "path": str(path)},
            )
        titles[task_id] = match.group("title")
        checked[task_id] = match.group("mark").lower() == "x"
    if not titles:
        raise QualificationError(
            "canonical task markdown contains no MSTR-000B task entries",
            code="task_gate.tasks_empty",
            details={"path": str(path)},
        )
    return titles, checked


def load_task_catalog(
    catalog_path: Path | None = None,
    *,
    repository_root: Path | None = None,
) -> TaskCatalog:
    """Load the B002 catalog and validate every generated TaskNode contract."""

    root = (repository_root or _REPOSITORY_ROOT).resolve()
    path = (catalog_path or (root / "configs" / "task-gate" / "mstr-000b.json")).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise QualificationError(
            "task catalog must remain inside the repository",
            code="task_gate.catalog_outside_repository",
            details={"path": str(path), "root": str(root)},
        ) from exc
    raw = _read_json_object(path, code="task_gate.catalog")
    if raw.get("catalog_version") != "mstr.task-catalog.v0":
        raise QualificationError(
            "unsupported task catalog version",
            code="task_gate.catalog_version",
            details={"value": raw.get("catalog_version")},
        )
    workstream_id = raw.get("workstream_id")
    tasks_file_raw = raw.get("tasks_file")
    defaults = raw.get("defaults")
    tasks = raw.get("tasks")
    unresolved = raw.get("unresolved_bindings", {})
    external_prerequisites = raw.get("external_prerequisites", {})
    if not isinstance(workstream_id, str) or not workstream_id:
        raise QualificationError(
            "catalog workstream_id is invalid",
            code="task_gate.catalog_workstream",
        )
    if not isinstance(tasks_file_raw, str) or not tasks_file_raw:
        raise QualificationError(
            "catalog tasks_file is invalid",
            code="task_gate.catalog_tasks_file",
        )
    if not isinstance(defaults, dict) or not isinstance(tasks, dict):
        raise QualificationError(
            "catalog defaults/tasks must be objects",
            code="task_gate.catalog_shape",
        )
    if not isinstance(unresolved, dict) or any(
        not isinstance(key, str) or not isinstance(value, str) for key, value in unresolved.items()
    ):
        raise QualificationError(
            "catalog unresolved_bindings must map task ids to explanations",
            code="task_gate.catalog_unresolved_shape",
        )
    if not isinstance(external_prerequisites, dict):
        raise QualificationError(
            "catalog external_prerequisites must be an object",
            code="task_gate.catalog_external_shape",
        )
    for external_task_id, binding in external_prerequisites.items():
        if not isinstance(external_task_id, str) or not re.fullmatch(
            r"[A-Z][0-9]{3}", external_task_id
        ):
            raise QualificationError(
                "external prerequisite id is invalid",
                code="task_gate.catalog_external_id",
                details={"task_id": external_task_id},
            )
        if external_task_id in tasks:
            raise QualificationError(
                "external prerequisite cannot shadow a catalog task",
                code="task_gate.catalog_external_shadow",
                details={"task_id": external_task_id},
            )
        if not isinstance(binding, dict):
            raise QualificationError(
                "external prerequisite binding must be an object",
                code="task_gate.catalog_external_binding",
                details={"task_id": external_task_id},
            )
        workstream = binding.get("workstream_id")
        external_tasks_file = binding.get("tasks_file")
        state_evidence = binding.get("state_evidence")
        evidence_outputs = binding.get("evidence_outputs")
        required_state = binding.get("required_state")
        if not isinstance(workstream, str) or not workstream:
            raise QualificationError(
                "external prerequisite workstream_id is invalid",
                code="task_gate.catalog_external_workstream",
                details={"task_id": external_task_id},
            )
        if not isinstance(external_tasks_file, str) or not external_tasks_file:
            raise QualificationError(
                "external prerequisite tasks_file is invalid",
                code="task_gate.catalog_external_tasks_file",
                details={"task_id": external_task_id},
            )
        if not isinstance(state_evidence, str) or not state_evidence:
            raise QualificationError(
                "external prerequisite state_evidence is invalid",
                code="task_gate.catalog_external_state_evidence",
                details={"task_id": external_task_id},
            )
        if (
            not isinstance(evidence_outputs, list)
            or not evidence_outputs
            or any(not isinstance(item, str) or not item for item in evidence_outputs)
            or state_evidence not in evidence_outputs
        ):
            raise QualificationError(
                "external prerequisite evidence_outputs are invalid",
                code="task_gate.catalog_external_evidence",
                details={"task_id": external_task_id},
            )
        if required_state != "COMPLETE_CANONICAL":
            raise QualificationError(
                "external prerequisite v0 requires COMPLETE_CANONICAL",
                code="task_gate.catalog_external_state",
                details={"task_id": external_task_id, "required_state": required_state},
            )
        _repository_path(root, external_tasks_file, field="external prerequisite tasks_file")
        _repository_path(root, state_evidence, field="external prerequisite state_evidence")
        for evidence_output in evidence_outputs:
            _repository_path(root, evidence_output, field="external prerequisite evidence")

    tasks_file = _repository_path(root, tasks_file_raw, field="tasks_file")
    contained_tasks_file = _contained_existing_path(root, tasks_file)
    if contained_tasks_file is None or not contained_tasks_file.is_file():
        raise QualificationError(
            "canonical task markdown must be a repository-contained regular file",
            code="task_gate.tasks_file_invalid",
            details={"path": str(tasks_file), "root": str(root)},
        )
    tasks_file = contained_tasks_file
    titles, checked = _parse_task_markdown(tasks_file)
    catalog_ids = set(tasks)
    unknown_unresolved = sorted(set(unresolved) - catalog_ids)
    if unknown_unresolved:
        raise QualificationError(
            "catalog unresolved_bindings reference unknown task ids",
            code="task_gate.catalog_unresolved_unknown",
            details={"task_ids": unknown_unresolved},
        )
    markdown_ids = set(titles)
    if catalog_ids != markdown_ids:
        raise QualificationError(
            "task catalog coverage differs from canonical task markdown",
            code="task_gate.catalog_coverage",
            details={
                "missing_from_catalog": sorted(markdown_ids - catalog_ids),
                "extra_in_catalog": sorted(catalog_ids - markdown_ids),
            },
        )

    nodes: dict[str, dict[str, Any]] = {}
    for task_id in sorted(tasks):
        override = tasks[task_id]
        if not isinstance(override, dict):
            raise QualificationError(
                "task catalog entry must be an object",
                code="task_gate.catalog_task_shape",
                details={"task_id": task_id},
            )
        fields = _merge_dicts(defaults, override)
        fields.update(
            {
                "schema_version": "mstr.task-node.v0",
                "task_id": task_id,
                "workstream_id": workstream_id,
                "title": titles[task_id],
            }
        )
        errors = validation_errors("mstr-task-node-v0", fields)
        if errors:
            raise QualificationError(
                "catalog generated an invalid TaskNode",
                code="task_gate.catalog_node_invalid",
                details={"task_id": task_id, "errors": list(errors)},
            )
        nodes[task_id] = fields
    return TaskCatalog(
        root,
        tasks_file,
        nodes,
        checked,
        dict(unresolved),
        {key: dict(value) for key, value in external_prerequisites.items()},
    )


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
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
            "unable to inspect repository Git state",
            code="task_gate.git_unavailable",
            details={"root": str(root), "args": list(args)},
        ) from exc


def _git_head(root: Path) -> str:
    completed = _run_git(root, "rev-parse", "HEAD")
    value = completed.stdout.strip().lower()
    if completed.returncode != 0 or not _HEX40_RE.fullmatch(value):
        raise QualificationError(
            "current Git HEAD is not a 40-hex commit identity",
            code="task_gate.git_head_invalid",
            details={"returncode": completed.returncode, "value": value},
        )
    return value


def _git_ref(root: Path, ref: str, *, code: str) -> str:
    completed = _run_git(root, "rev-parse", "--verify", ref)
    value = completed.stdout.strip().lower()
    if completed.returncode != 0 or not _HEX40_RE.fullmatch(value):
        raise QualificationError(
            "required canonical Git ref is unavailable or invalid",
            code=code,
            details={"ref": ref, "returncode": completed.returncode, "value": value},
        )
    return value


def _trusted_canonical_main(root: Path) -> str:
    """Bind eligibility to canonical main refs without performing network I/O.

    Execution governance must refresh and verify ``origin/main`` against live repository
    truth immediately before invoking this offline gate. The gate then refuses any
    checkout where local ``main``, cached ``origin/main``, and ``HEAD`` do not agree.
    """
    head = _git_head(root)
    local_main = _git_ref(root, "refs/heads/main", code="task_gate.main_ref_invalid")
    origin_main = _git_ref(
        root,
        "refs/remotes/origin/main",
        code="task_gate.origin_main_ref_invalid",
    )
    if local_main != origin_main:
        raise QualificationError(
            "local main does not match the refreshed origin/main identity",
            code="task_gate.main_ref_mismatch",
            details={"main": local_main, "origin_main": origin_main},
        )
    if head != local_main:
        raise QualificationError(
            "task eligibility must execute at the canonical main commit",
            code="task_gate.not_canonical_main",
            details={"head": head, "canonical_main": local_main},
        )
    status = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        raise QualificationError(
            "unable to verify clean canonical checkout",
            code="task_gate.git_status",
            details={"returncode": status.returncode},
        )
    if status.stdout.strip():
        raise QualificationError(
            "task eligibility refuses a dirty canonical checkout",
            code="task_gate.dirty_checkout",
            details={"entries": status.stdout.splitlines()},
        )
    return head
def _node_sha256(node: dict[str, Any]) -> str:
    payload = json.dumps(node, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _declared_terminal_state(node: dict[str, Any]) -> bool:
    state = node["canonical_state"]
    return state in node["closeout_rule"]["terminal_states"]


def _prerequisite_completion_state(node: dict[str, Any]) -> bool:
    return (
        _declared_terminal_state(node)
        and node["canonical_state"] != "SUPERSEDED_CANONICAL"
    )


def _checkbox_consistent(node: dict[str, Any], checked: bool | None) -> bool:
    if checked is None:
        return False
    return checked is _declared_terminal_state(node)


def _contained_existing_path(root: Path, candidate: Path) -> Path | None:
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
    return resolved


def _path_pattern_present(root: Path, raw: str) -> bool:
    path = _repository_path(root, raw, field="task output")
    if any(marker in raw for marker in ("*", "?", "[")):
        matches = (Path(match) for match in glob.glob(str(path), recursive=True))
        return any(
            _contained_existing_path(root, match) is not None
            for match in matches
        )
    return _contained_existing_path(root, path) is not None

def _required_closeout_paths_present(root: Path, node: dict[str, Any]) -> tuple[bool, list[str]]:
    rule = node["closeout_rule"]
    required: list[str] = []
    if rule["require_all_outputs"]:
        required.extend(node["outputs"])
    if rule["require_all_evidence_outputs"]:
        required.extend(node["evidence_outputs"])
    missing = [raw for raw in required if not _path_pattern_present(root, raw)]
    return not missing, missing


def _read_bound_json_artifact(
    root: Path,
    directory: str,
    binding_id: str,
) -> dict[str, Any] | None:
    if not _BINDING_ID_RE.fullmatch(binding_id):
        return None
    path = root / "artifacts" / directory / f"{binding_id}.json"
    resolved = _contained_existing_path(root, path)
    if resolved is None or not resolved.is_file():
        return None
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _authority_ceiling_valid(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    cost_model = value.get("cost_model")
    if not isinstance(cost_model, str) or not cost_model.strip():
        return False
    limits = value.get("limits")
    if not isinstance(limits, list) or not limits:
        return False
    for limit in limits:
        if not isinstance(limit, dict):
            return False
        resource = limit.get("resource")
        unit = limit.get("unit")
        maximum = limit.get("max")
        if not isinstance(resource, str) or not resource.strip():
            return False
        if not isinstance(unit, str) or not unit.strip():
            return False
        if isinstance(maximum, bool) or not isinstance(maximum, (int, float)):
            return False
        if not math.isfinite(float(maximum)) or maximum < 0:
            return False
    return True


def _authority_observed(root: Path, task_id: str, effect: str, authority_id: str) -> bool:
    """Verify one existing canonical authority envelope; never create authority."""
    data = _read_bound_json_artifact(root, "authorities", authority_id)
    if data is None:
        return False
    scope = data.get("scope")
    return bool(
        data.get("authority_id") == authority_id
        and data.get("task_id") == task_id
        and data.get("external_effect_class") == effect
        and data.get("status") == "AUTHORIZED_CANONICAL"
        and isinstance(scope, dict)
        and bool(scope)
        and _authority_ceiling_valid(data.get("cost_resource_ceiling"))
    )


def _candidate_pool_observed(root: Path, requirement_id: str) -> bool:
    data = _read_bound_json_artifact(root, "decisions", requirement_id)
    if data is None or data.get("stable_pool") is not True:
        return False
    observed = data.get("decision_id", data.get("candidate_pool_id"))
    return observed == requirement_id

def _external_task_checked(
    catalog: TaskCatalog, task_id: str, binding: dict[str, Any]
) -> bool | None:
    raw = binding["tasks_file"]
    path = _repository_path(catalog.repository_root, raw, field="external prerequisite tasks_file")
    resolved = _contained_existing_path(catalog.repository_root, path)
    if resolved is None or not resolved.is_file():
        return None
    try:
        external_text = resolved.read_text(encoding="utf-8")
    except OSError:
        return None
    pattern = re.compile(
        rf"^- \[(?P<mark>[ xX])\] \*\*{re.escape(task_id)} .+?\.\*\*",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(external_text))
    if len(matches) != 1:
        return None
    return matches[0].group("mark").lower() == "x"


def _external_evidence_claims(
    catalog: TaskCatalog, task_id: str, binding: dict[str, Any]
) -> tuple[bool, bool]:
    raw = binding["state_evidence"]
    path = _repository_path(
        catalog.repository_root, raw, field="external prerequisite state_evidence"
    )
    resolved = _contained_existing_path(catalog.repository_root, path)
    if resolved is None or not resolved.is_file():
        return False, False
    try:
        evidence_text = resolved.read_text(encoding="utf-8")
    except OSError:
        return False, False
    task_match = re.search(
        r"^\*\*Task:\*\*\s*`(?P<task>[^`]+)`\s*$", evidence_text, re.MULTILINE
    )
    expected_task_values = {task_id, f"{binding['workstream_id']} / {task_id}"}
    identity_declared = bool(
        task_match is not None and task_match.group("task") in expected_task_values
    )
    required_state = binding["required_state"]
    state_declared = bool(
        re.search(
            rf"^\*\*State:\*\*\s*`{re.escape(required_state)}`\s*$",
            evidence_text,
            re.MULTILINE,
        )
    )
    return identity_declared, state_declared


def _external_prerequisite_result(
    catalog: TaskCatalog, task_id: str, binding: dict[str, Any]
) -> dict[str, Any]:
    checked = _external_task_checked(catalog, task_id, binding)
    required_state = binding["required_state"]
    identity_declared, state_declared = _external_evidence_claims(
        catalog, task_id, binding
    )
    missing = [
        raw
        for raw in binding["evidence_outputs"]
        if not _path_pattern_present(catalog.repository_root, raw)
    ]
    evidence_present = not missing and identity_declared and state_declared
    reasons: list[str] = []
    if checked is not True:
        reasons.append("prerequisite.state_checkbox_conflict")
    if not identity_declared:
        reasons.append("prerequisite.external_identity_unproven")
    if not state_declared:
        reasons.append("prerequisite.external_state_unproven")
    if missing:
        reasons.append("prerequisite.required_artifact_missing")
    satisfied = checked is True and evidence_present
    return {
        "task_id": task_id,
        "required_state": required_state,
        "observed_state": required_state if state_declared else None,
        "evidence_present": evidence_present,
        "satisfied": satisfied,
        "reasons": reasons + [f"missing:{item}" for item in missing],
    }


def _prerequisite_result(catalog: TaskCatalog, task_id: str) -> dict[str, Any]:
    node = catalog.nodes.get(task_id)
    if node is None:
        external = catalog.external_prerequisites.get(task_id)
        if external is not None:
            return _external_prerequisite_result(catalog, task_id, external)
        return {
            "task_id": task_id,
            "required_state": "COMPLETE_CANONICAL",
            "observed_state": None,
            "evidence_present": False,
            "satisfied": False,
            "reasons": ["prerequisite.missing_task_binding"],
        }
    state = node["canonical_state"]
    consistent = _checkbox_consistent(node, catalog.checked.get(task_id))
    evidence_present, missing = _required_closeout_paths_present(catalog.repository_root, node)
    terminal = _prerequisite_completion_state(node)
    reasons: list[str] = []
    if not terminal:
        reasons.append("prerequisite.not_terminal")
    if not consistent:
        reasons.append("prerequisite.state_checkbox_conflict")
    if not evidence_present:
        reasons.append("prerequisite.required_artifact_missing")
    required_state = state if terminal else "COMPLETE_CANONICAL"
    return {
        "task_id": task_id,
        "required_state": required_state,
        "observed_state": state,
        "evidence_present": evidence_present,
        "satisfied": terminal and consistent and evidence_present,
        "reasons": reasons + [f"missing:{item}" for item in missing],
    }


def diagnose_task_node(
    node: dict[str, Any],
    *,
    canonical_main: str,
) -> dict[str, Any]:
    """Return schema-valid ``eligible=false`` diagnostics for an invalid TaskNode.

    B001's eligibility schema requires string identities when authority or a
    candidate pool is required, even when the source TaskNode omitted the
    required binding. Stable diagnostic sentinels are therefore used only in
    an ineligible result; they are never treated as observed authority/pool.
    """

    if not _HEX40_RE.fullmatch(canonical_main):
        raise QualificationError(
            "canonical_main must be a 40-hex commit identity",
            code="task_gate.canonical_main_invalid",
        )
    errors = validation_errors("mstr-task-node-v0", node)
    if not errors:
        raise QualificationError(
            "diagnose_task_node requires an invalid TaskNode",
            code="task_gate.diagnostic_valid_node",
        )
    task_id_raw = node.get("task_id")
    task_id = task_id_raw if isinstance(task_id_raw, str) and task_id_raw else "INVALID_TASK"
    effect = node.get("external_effect_class")
    authority_required = effect in _GATED_EFFECTS
    authority_raw = node.get("required_authority_id")
    authority_id = (
        authority_raw
        if authority_required and isinstance(authority_raw, str) and authority_raw
        else _MISSING_AUTHORITY_SENTINEL if authority_required else None
    )
    pool_required = node.get("candidate_dependent") is True
    pool_raw = node.get("candidate_pool_requirement_id")
    requirement_id = (
        pool_raw
        if pool_required and isinstance(pool_raw, str) and pool_raw
        else _MISSING_POOL_SENTINEL if pool_required else None
    )
    result = {
        "schema_version": "mstr.task-eligibility.v0",
        "task_id": task_id,
        "task_node_schema_version": "mstr.task-node.v0",
        "task_node_sha256": _node_sha256(node),
        "canonical_main": canonical_main,
        "eligible": False,
        "prerequisite_results": [],
        "authority_result": {
            "required": authority_required,
            "authority_id": authority_id,
            "satisfied": False if authority_required else True,
            "reasons": ["authority.required_binding_missing"] if authority_required else [],
        },
        "supersession_result": {
            "superseded": False,
            "superseded_by": [],
            "satisfied": False,
            "reasons": ["task_node.invalid"],
        },
        "state_consistency_result": {
            "observed_state": None,
            "satisfied": False,
            "reasons": ["task_node.invalid"],
        },
        "candidate_pool_result": {
            "required": pool_required,
            "requirement_id": requirement_id,
            "observed_pool_id": None,
            "satisfied": False if pool_required else True,
            "reasons": ["candidate_pool.required_binding_missing"] if pool_required else [],
        },
        "semantic_checks": {
            "task_node_binding_verified": False,
            "prerequisite_set_complete": False,
            "prerequisite_states_satisfied": False,
            "authority_requirement_complete": not authority_required,
            "candidate_pool_requirement_complete": not pool_required,
            "supersession_check_complete": False,
            "state_consistency_check_complete": False,
        },
        "reasons": ["task_node.invalid", *[f"schema:{error}" for error in errors]],
    }
    validate_instance("mstr-task-eligibility-v0", result)
    return result


def evaluate_task_snapshot(
    task_id: str,
    *,
    repository_root: Path | None = None,
    catalog_path: Path | None = None,
    canonical_main: str,
) -> dict[str, Any]:
    """Evaluate a supplied snapshot without claiming current-main authority."""
    root = (repository_root or _REPOSITORY_ROOT).resolve()
    main_sha = canonical_main
    if not _HEX40_RE.fullmatch(main_sha):
        raise QualificationError(
            "canonical main identity must be 40 lowercase hex",
            code="task_gate.canonical_main_invalid",
            details={"value": main_sha},
        )
    catalog = load_task_catalog(catalog_path, repository_root=root)
    node = catalog.nodes.get(task_id)
    if node is None:
        raise QualificationError(
            "unknown task id",
            code="task_gate.task_unknown",
            details={"task_id": task_id, "known": sorted(catalog.nodes)},
        )

    prerequisite_results = [
        _prerequisite_result(catalog, predecessor) for predecessor in node["prerequisites"]
    ]
    prerequisite_set_complete = all(
        predecessor in catalog.nodes or predecessor in catalog.external_prerequisites
        for predecessor in node["prerequisites"]
    )
    prerequisites_satisfied = all(item["satisfied"] for item in prerequisite_results)

    effect = node["external_effect_class"]
    authority_required = effect in _GATED_EFFECTS
    authority_id = node.get("required_authority_id")
    authority_satisfied = not authority_required
    authority_reasons: list[str] = []
    if authority_required:
        if not isinstance(authority_id, str) or not authority_id:
            authority_id = _MISSING_AUTHORITY_SENTINEL
            authority_reasons.append("authority.required_binding_missing")
        elif _authority_observed(catalog.repository_root, task_id, effect, authority_id):
            authority_satisfied = True
        else:
            authority_reasons.append("authority.canonical_envelope_missing_or_invalid")

    pool_required = bool(node["candidate_dependent"])
    requirement_id = node.get("candidate_pool_requirement_id")
    pool_satisfied = not pool_required
    observed_pool_id: str | None = None
    pool_reasons: list[str] = []
    if pool_required:
        if not isinstance(requirement_id, str) or not requirement_id:
            requirement_id = _MISSING_POOL_SENTINEL
            pool_reasons.append("candidate_pool.required_binding_missing")
        elif _candidate_pool_observed(catalog.repository_root, requirement_id):
            observed_pool_id = requirement_id
            pool_satisfied = True
        else:
            pool_reasons.append("candidate_pool.canonical_decision_missing_or_invalid")

    superseded_by = list(node["superseded_by"])
    superseded = node["canonical_state"] == "SUPERSEDED_CANONICAL" or bool(superseded_by)
    supersession_satisfied = not superseded
    supersession_reasons = [] if supersession_satisfied else ["task.superseded"]

    checkbox_consistent = _checkbox_consistent(node, catalog.checked.get(task_id))
    state_reasons = [] if checkbox_consistent else ["task.state_checkbox_conflict"]

    reasons: list[str] = []
    if node["canonical_state"] == "BLOCKED":
        reasons.append("task.blocked")
    elif _declared_terminal_state(node):
        reasons.append("task.already_terminal")
    elif node["canonical_state"] != "PENDING" and node["canonical_state"] != "ACTIVE":
        reasons.append("task.state_not_executable")
    if task_id in catalog.unresolved_bindings:
        reasons.append("task.unresolved_binding")
    for item in prerequisite_results:
        if not item["satisfied"]:
            reasons.append(f"prerequisite.unsatisfied:{item['task_id']}")
    if not authority_satisfied:
        reasons.extend(authority_reasons)
    if not pool_satisfied:
        reasons.extend(pool_reasons)
    if not supersession_satisfied:
        reasons.extend(supersession_reasons)
    if not checkbox_consistent:
        reasons.extend(state_reasons)
    reasons = sorted(set(reasons))

    semantic_checks = {
        "task_node_binding_verified": True,
        "prerequisite_set_complete": prerequisite_set_complete,
        "prerequisite_states_satisfied": prerequisites_satisfied,
        "authority_requirement_complete": authority_satisfied,
        "candidate_pool_requirement_complete": pool_satisfied,
        "supersession_check_complete": supersession_satisfied,
        "state_consistency_check_complete": checkbox_consistent,
    }
    eligible = (
        node["canonical_state"] in {"PENDING", "ACTIVE"}
        and task_id not in catalog.unresolved_bindings
        and all(semantic_checks.values())
        and not reasons
    )

    result = {
        "schema_version": "mstr.task-eligibility.v0",
        "task_id": task_id,
        "task_node_schema_version": "mstr.task-node.v0",
        "task_node_sha256": _node_sha256(node),
        "canonical_main": main_sha,
        "eligible": eligible,
        "prerequisite_results": prerequisite_results,
        "authority_result": {
            "required": authority_required,
            "authority_id": authority_id if authority_required else None,
            "satisfied": authority_satisfied,
            "reasons": authority_reasons,
        },
        "supersession_result": {
            "superseded": superseded,
            "superseded_by": superseded_by if superseded else [],
            "satisfied": supersession_satisfied,
            "reasons": supersession_reasons,
        },
        "state_consistency_result": {
            "observed_state": node["canonical_state"],
            "satisfied": checkbox_consistent,
            "reasons": state_reasons,
        },
        "candidate_pool_result": {
            "required": pool_required,
            "requirement_id": requirement_id if pool_required else None,
            "observed_pool_id": observed_pool_id,
            "satisfied": pool_satisfied,
            "reasons": pool_reasons,
        },
        "semantic_checks": semantic_checks,
        "reasons": reasons,
    }
    validate_instance("mstr-task-eligibility-v0", result)
    return result


def evaluate_task_eligibility(
    task_id: str,
    *,
    repository_root: Path | None = None,
    catalog_path: Path | None = None,
) -> dict[str, Any]:
    """Evaluate one task against the verified canonical-main checkout."""
    root = (repository_root or _REPOSITORY_ROOT).resolve()
    canonical_main = _trusted_canonical_main(root)
    return evaluate_task_snapshot(
        task_id,
        repository_root=root,
        catalog_path=catalog_path,
        canonical_main=canonical_main,
    )
