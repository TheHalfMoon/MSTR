"""Offline, fail-closed task eligibility evaluation for MSTR-000B B002.

The gate reads only repository-local canonical metadata. It never mutates task
state, creates authority, contacts a remote service, or infers permission from
an identifier alone. The caller is responsible for running the command against
the exact canonical-main checkout required by repository governance; the result
binds itself to the checked-out Git SHA so that claim is externally verifiable.
"""

from __future__ import annotations

import glob
import hashlib
import json
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

    tasks_file = _repository_path(root, tasks_file_raw, field="tasks_file")
    titles, checked = _parse_task_markdown(tasks_file)
    catalog_ids = set(tasks)
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
    return TaskCatalog(root, tasks_file, nodes, checked, dict(unresolved))


def _git_head(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise QualificationError(
            "unable to resolve current Git HEAD",
            code="task_gate.git_head",
            details={"root": str(root)},
        ) from exc
    value = completed.stdout.strip().lower()
    if completed.returncode != 0 or not _HEX40_RE.fullmatch(value):
        raise QualificationError(
            "current Git HEAD is not a 40-hex commit identity",
            code="task_gate.git_head_invalid",
            details={"returncode": completed.returncode, "value": value},
        )
    return value


def _node_sha256(node: dict[str, Any]) -> str:
    payload = json.dumps(node, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _terminal_state(state: object) -> bool:
    return state in _TERMINAL_COMPLETE or (
        isinstance(state, str) and state.startswith("NOT_REQUIRED")
    )


def _checkbox_consistent(state: object, checked: bool | None) -> bool:
    if checked is None:
        return False
    return checked is _terminal_state(state)


def _path_pattern_present(root: Path, raw: str) -> bool:
    path = _repository_path(root, raw, field="task output")
    if any(marker in raw for marker in ("*", "?", "[")):
        return bool(glob.glob(str(path), recursive=True))
    return path.exists()


def _required_closeout_paths_present(root: Path, node: dict[str, Any]) -> tuple[bool, list[str]]:
    rule = node["closeout_rule"]
    required: list[str] = []
    if rule["require_all_outputs"]:
        required.extend(node["outputs"])
    if rule["require_all_evidence_outputs"]:
        required.extend(node["evidence_outputs"])
    missing = [raw for raw in required if not _path_pattern_present(root, raw)]
    return not missing, missing


def _authority_observed(root: Path, task_id: str, effect: str, authority_id: str) -> bool:
    """Verify a canonical repository authority envelope; never create one.

    B002 recognizes only an exact repository-local envelope at
    ``artifacts/authorities/<authority_id>.json``. The envelope must bind the
    same task/effect and explicitly record ``AUTHORIZED_CANONICAL``. No such
    envelope is created by B002.
    """

    path = root / "artifacts" / "authorities" / f"{authority_id}.json"
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(
        isinstance(data, dict)
        and data.get("authority_id") == authority_id
        and data.get("task_id") == task_id
        and data.get("external_effect_class") == effect
        and data.get("status") == "AUTHORIZED_CANONICAL"
        and isinstance(data.get("scope"), dict)
    )


def _candidate_pool_observed(root: Path, requirement_id: str) -> bool:
    path = root / "artifacts" / "decisions" / f"{requirement_id}.json"
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict) or data.get("stable_pool") is not True:
        return False
    observed = data.get("decision_id", data.get("candidate_pool_id"))
    return observed == requirement_id


def _prerequisite_result(catalog: TaskCatalog, task_id: str) -> dict[str, Any]:
    node = catalog.nodes.get(task_id)
    if node is None:
        return {
            "task_id": task_id,
            "required_state": "COMPLETE_CANONICAL",
            "observed_state": None,
            "evidence_present": False,
            "satisfied": False,
            "reasons": ["prerequisite.missing_task_binding"],
        }
    state = node["canonical_state"]
    consistent = _checkbox_consistent(state, catalog.checked.get(task_id))
    evidence_present, missing = _required_closeout_paths_present(catalog.repository_root, node)
    terminal = _terminal_state(state) and state != "SUPERSEDED_CANONICAL"
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


def evaluate_task_eligibility(
    task_id: str,
    *,
    repository_root: Path | None = None,
    catalog_path: Path | None = None,
    canonical_main: str | None = None,
) -> dict[str, Any]:
    """Evaluate one task against repository-local canonical state without mutation."""

    catalog = load_task_catalog(catalog_path, repository_root=repository_root)
    node = catalog.nodes.get(task_id)
    if node is None:
        raise QualificationError(
            "unknown task id",
            code="task_gate.task_unknown",
            details={"task_id": task_id, "known": sorted(catalog.nodes)},
        )
    main_sha = canonical_main or _git_head(catalog.repository_root)
    if not _HEX40_RE.fullmatch(main_sha):
        raise QualificationError(
            "canonical main identity must be 40 lowercase hex",
            code="task_gate.canonical_main_invalid",
            details={"value": main_sha},
        )

    prerequisite_results = [
        _prerequisite_result(catalog, predecessor) for predecessor in node["prerequisites"]
    ]
    prerequisite_set_complete = all(
        predecessor in catalog.nodes for predecessor in node["prerequisites"]
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

    checkbox_consistent = _checkbox_consistent(
        node["canonical_state"], catalog.checked.get(task_id)
    )
    state_reasons = [] if checkbox_consistent else ["task.state_checkbox_conflict"]

    reasons: list[str] = []
    if node["canonical_state"] == "BLOCKED":
        reasons.append("task.blocked")
    elif _terminal_state(node["canonical_state"]):
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
