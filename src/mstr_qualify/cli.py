"""Dependency-light, offline qualification CLI for MSTR-000 (T010).

Command families implemented by this task:

```text
mstr-qualify validate [paths...]
mstr-qualify rights <candidate-config>
mstr-qualify candidate static <candidate-config>
mstr-qualify task eligible <TASK_ID> --canonical-main <SHA>
mstr-qualify manifest validate <manifest> [--kind {candidate,task,benchmark}]
```

Exit-code contract (deterministic and testable):

```text
0 = the requested check or decision passed
1 = the requested check or decision ran and failed (checked artifact is
    schema-invalid, rights-ineligible, or otherwise fail-closed)
2 = invocation/configuration/environment error (missing file, unknown
    command, unreadable input, unsupported kind)
```

Offline discipline: every command performs local filesystem reads only.
No command downloads weights, accepts gated terms, contacts a provider,
executes a model, or performs any outbound network access. `candidate
static` reports a static qualification summary; it never mutates candidate
records, writes artifacts, or changes admission state — that authority
belongs to later canonical tasks (T012+).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from . import __version__
from .errors import QualificationError
from .ids import sha256_file, stable_id
from .manifests import load_manifest
from .rights import ComponentRightsResult, evaluate_component_rights
from .schemas import (
    DEFAULT_SCHEMA_DIR,
    SCHEMA_FILES,
    load_schema,
    validation_errors,
)
from .task_gate import evaluate_task_eligibility

_EXIT_OK = 0
_EXIT_FAIL_CLOSED = 1
_EXIT_ERROR = 2

# Manifest kinds accepted by `load_manifest`, keyed by their canonical
# `schema_version` values for auto-detection.
_MANIFEST_KINDS = ("candidate", "task", "benchmark")
_SCHEMA_VERSION_TO_KIND = {
    "mstr.candidate.v1": "candidate",
    "mstr.task.v1": "task",
    "mstr.benchmark.v1": "benchmark",
}
_SCHEMA_VERSION_TO_SCHEMA_NAME = {
    "mstr.run.v1": "run-evidence",
    "mstr.interaction.v1": "interaction-contract",
    # T027 weight-access preflight manifest: preparation-only contract.
    "mstr.weight-access-manifest.v1": "weight-access-manifest",
    # MSTR-000B B001 machine-task contracts.
    "mstr.task-node.v0": "mstr-task-node-v0",
    "mstr.task-eligibility.v0": "mstr-task-eligibility-v0",
}

_REPOSITORY_ROOT = DEFAULT_SCHEMA_DIR.parent
_SCHEMA_FIXTURE_ROOT = _REPOSITORY_ROOT / "tests" / "fixtures" / "schemas"
_VALID_FIXTURES = _SCHEMA_FIXTURE_ROOT / "valid" / "fixtures.json"
_INVALID_FIXTURES = _SCHEMA_FIXTURE_ROOT / "invalid" / "fixtures.json"


class _CheckedFailure(Exception):
    """Internal signal: a requested check ran and failed (exit code 1)."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        super().__init__(payload.get("code", "checked.failure"))


def _payload(command: str, status: str, **fields: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"command": command, "status": status}
    data.update(fields)
    return data


def _dump(value: dict[str, Any]) -> str:
    """Serialize command output deterministically."""

    return json.dumps(value, sort_keys=True, indent=2)


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise QualificationError(
            "unable to read input file",
            code="cli.input_read",
            details={"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise QualificationError(
            "input is not valid JSON",
            code="cli.input_json_invalid",
            details={"path": str(path), "line": exc.lineno, "column": exc.colno},
        ) from exc
    if not isinstance(decoded, dict):
        raise QualificationError(
            "input root must be a JSON object",
            code="cli.input_root_type",
            details={"path": str(path)},
        )
    return decoded


def _require_existing_file(path: Path, *, option: str) -> None:
    if not path.is_file():
        raise QualificationError(
            f"{option} must be an existing file",
            code="cli.input_missing",
            details={option: str(path)},
        )


def _schema_version_of(data: dict[str, Any], path: Path) -> str | None:
    value = data.get("schema_version")
    if value is None:
        return None
    if not isinstance(value, str):
        raise QualificationError(
            "schema_version must be a string when present",
            code="cli.schema_version_type",
            details={"path": str(path), "value": repr(value)},
        )
    return value


def _checked_qualification_error(
    command: str,
    path: Path | None,
    exc: QualificationError,
) -> _CheckedFailure:
    fields: dict[str, Any] = {
        "code": exc.code,
        "message": exc.message,
        "details": dict(exc.details),
    }
    if path is not None:
        fields["path"] = str(path)
    return _CheckedFailure(_payload(command, "fail", **fields))


def _rights_summary(
    candidate_id: str,
    rights_data: Any,
) -> tuple[ComponentRightsResult, dict[str, Any]]:
    """Recompute primary eligibility from evidence facts via T006."""

    if not isinstance(rights_data, dict):
        raise QualificationError(
            "candidate record has no rights object",
            code="cli.rights_missing",
            details={"candidate_id": candidate_id},
        )
    result = evaluate_component_rights(candidate_id, rights_data)
    fields = {
        "candidate_id": result.component_id,
        "computed_decision": result.computed_decision,
        "eligible_for_primary": result.eligible_for_primary,
        "reason_codes": list(result.reason_codes),
    }
    return result, fields


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def _validate_registered_schemas() -> list[str]:
    checked = sorted(SCHEMA_FILES)
    for name in checked:
        load_schema(name)
    return checked


def _dedicated_fixture(kind: str, schema_name: str) -> object | None:
    """Load a per-schema fixture when present, failing closed on malformed JSON."""

    path = _SCHEMA_FIXTURE_ROOT / kind / f"{schema_name}.json"
    if not path.is_file():
        return None
    try:
        parsed: object = json.loads(path.read_text(encoding="utf-8"))
        return parsed
    except OSError as exc:
        raise QualificationError(
            "canonical dedicated schema fixture is unreadable",
            code="cli.fixture_read",
            details={"schema": schema_name, "kind": kind, "path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise QualificationError(
            "canonical dedicated schema fixture is not valid JSON",
            code="cli.fixture_json_invalid",
            details={
                "schema": schema_name,
                "kind": kind,
                "path": str(path),
                "reason": exc.msg,
            },
        ) from exc


def _fixture_instance(
    kind: str,
    schema_name: str,
    aggregate: dict[str, Any],
) -> object:
    """Resolve dedicated-first fixtures while preserving the legacy aggregate fallback."""

    dedicated = _dedicated_fixture(kind, schema_name)
    if dedicated is not None:
        return dedicated
    if schema_name in aggregate:
        return aggregate[schema_name]
    raise QualificationError(
        "registered schema has no canonical fixture",
        code="cli.fixture_missing",
        details={"schema": schema_name, "kind": kind},
    )


def _validate_fixture_sets() -> tuple[int, int]:
    """Validate one passing and one failing canonical fixture for every schema."""

    try:
        valid_fixtures = json.loads(_VALID_FIXTURES.read_text(encoding="utf-8"))
        invalid_fixtures = json.loads(_INVALID_FIXTURES.read_text(encoding="utf-8"))
    except OSError as exc:
        raise QualificationError(
            "canonical schema fixtures are missing from this checkout",
            code="cli.fixtures_missing",
            details={
                "expected_valid": str(_VALID_FIXTURES),
                "expected_invalid": str(_INVALID_FIXTURES),
            },
        ) from exc
    except json.JSONDecodeError as exc:
        raise QualificationError(
            "canonical schema fixtures are not valid JSON",
            code="cli.fixtures_json_invalid",
            details={"reason": exc.msg},
        ) from exc
    if not isinstance(valid_fixtures, dict) or not isinstance(invalid_fixtures, dict):
        raise QualificationError(
            "fixture sets must map schema names to instances",
            code="cli.fixtures_root_type",
        )

    valid_passed = 0
    invalid_rejected = 0
    for name in sorted(SCHEMA_FILES):
        valid_instance = _fixture_instance("valid", name, valid_fixtures)
        errors = validation_errors(name, valid_instance)
        if errors:
            raise _CheckedFailure(
                _payload(
                    "validate",
                    "fail",
                    code="cli.fixture_should_pass",
                    schema=name,
                    errors=list(errors),
                )
            )
        valid_passed += 1

        invalid_instance = _fixture_instance("invalid", name, invalid_fixtures)
        if not validation_errors(name, invalid_instance):
            raise _CheckedFailure(
                _payload(
                    "validate",
                    "fail",
                    code="cli.fixture_should_fail",
                    schema=name,
                )
            )
        invalid_rejected += 1
    return valid_passed, invalid_rejected


def _validate_file(path: Path) -> dict[str, Any]:
    """Validate one JSON file against its auto-detected canonical contract."""

    data = _read_json_object(path)
    version = _schema_version_of(data, path)
    if version is None:
        raise _CheckedFailure(
            _payload(
                "validate",
                "fail",
                path=str(path),
                code="cli.schema_version_missing",
                message="file has no schema_version to detect its contract",
            )
        )

    kind = _SCHEMA_VERSION_TO_KIND.get(version)
    schema_name = _SCHEMA_VERSION_TO_SCHEMA_NAME.get(version)
    try:
        if kind is not None:
            load_manifest(kind, path)
        elif schema_name is not None:
            from .schemas import validate_instance

            validate_instance(schema_name, data)
        else:
            raise QualificationError(
                "unsupported schema_version",
                code="cli.schema_version_unknown",
                details={
                    "path": str(path),
                    "value": version,
                    "supported": sorted(
                        {*_SCHEMA_VERSION_TO_KIND, *_SCHEMA_VERSION_TO_SCHEMA_NAME}
                    ),
                },
            )
    except QualificationError as exc:
        raise _checked_qualification_error("validate", path, exc) from exc
    return _payload("validate", "pass", path=str(path), schema_version=version)


def run_validate(paths: Sequence[Path]) -> tuple[int, dict[str, Any]]:
    """Self-check registered schemas plus canonical fixtures, or explicit files."""

    if not paths:
        checked = _validate_registered_schemas()
        valid_passed, invalid_rejected = _validate_fixture_sets()
        payload = _payload(
            "validate",
            "pass",
            schemas_checked=checked,
            valid_fixtures_passed=valid_passed,
            invalid_fixtures_rejected=invalid_rejected,
        )
        return _EXIT_OK, payload

    results: list[dict[str, Any]] = []
    failed = False
    for raw_path in paths:
        path = Path(raw_path)
        _require_existing_file(path, option="path")
        try:
            entry = _validate_file(path)
        except _CheckedFailure as failure:
            entry = failure.payload
            failed = True
        results.append(entry)
    payload = _payload("validate", "fail" if failed else "pass", files=results)
    exit_code = _EXIT_FAIL_CLOSED if failed else _EXIT_OK
    return exit_code, payload


# ---------------------------------------------------------------------------
# rights / candidate static
# ---------------------------------------------------------------------------


def _load_candidate_checked(path: Path) -> Any:
    try:
        return load_manifest("candidate", path)
    except QualificationError as exc:
        raise _checked_qualification_error("candidate", path, exc) from exc


def run_rights(path: Path) -> tuple[int, dict[str, Any]]:
    """Recompute primary rights eligibility for one candidate config."""

    _require_existing_file(path, option="candidate-config")
    loaded = _load_candidate_checked(path)
    _, summary = _rights_summary(str(loaded.data["candidate_id"]), loaded.data.get("rights"))
    eligible = bool(summary["eligible_for_primary"])
    payload = _payload("rights", "pass" if eligible else "fail", **summary)
    exit_code = _EXIT_OK if eligible else _EXIT_FAIL_CLOSED
    return exit_code, payload


def run_candidate_static(path: Path) -> tuple[int, dict[str, Any]]:
    """Report a static qualification summary for one candidate without weights.

    Schema validity is enforced by the loader. Primary rights are recomputed
    from evidence facts (never trusting the declared `decision`). The output
    binds the summary to the exact source-file SHA-256 and a stable record ID.
    """

    _require_existing_file(path, option="candidate-config")
    loaded = _load_candidate_checked(path)
    source_sha256 = sha256_file(path)
    _, rights_fields = _rights_summary(str(loaded.data["candidate_id"]), loaded.data.get("rights"))
    static_qualified = bool(rights_fields["eligible_for_primary"])
    payload = _payload(
        "candidate",
        "static_qualified" if static_qualified else "static_failed",
        candidate_subcommand="static",
        upstream_id=str(loaded.data["upstream_id"]),
        upstream_revision=str(loaded.data["upstream_revision"]),
        candidate_role=str(loaded.data["candidate_role"]),
        recorded_status=str(loaded.data["status"]),
        source_sha256=source_sha256,
        static_record_id=stable_id("mstr.static-candidate", source_sha256),
        weights_accessed=False,
        **rights_fields,
    )
    exit_code = _EXIT_OK if static_qualified else _EXIT_FAIL_CLOSED
    return exit_code, payload


# ---------------------------------------------------------------------------
# manifest validate
# ---------------------------------------------------------------------------


def run_manifest_validate(path: Path, kind: str | None) -> tuple[int, dict[str, Any]]:
    """Validate one task/candidate/benchmark manifest through T008 loaders."""

    _require_existing_file(path, option="manifest")
    detected: str | None = kind
    if detected is None:
        data = _read_json_object(path)
        version = _schema_version_of(data, path)
        detected = _SCHEMA_VERSION_TO_KIND.get(version or "")
        if detected is None:
            raise QualificationError(
                "cannot determine manifest kind; pass --kind explicitly",
                code="cli.manifest_kind_unknown",
                details={
                    "path": str(path),
                    "schema_version": version,
                    "supported_versions": sorted(_SCHEMA_VERSION_TO_KIND),
                    "kinds": list(_MANIFEST_KINDS),
                },
            )
    if detected not in _MANIFEST_KINDS:
        raise QualificationError(
            "unsupported --kind value",
            code="cli.manifest_kind_unsupported",
            details={"kind": detected, "allowed": list(_MANIFEST_KINDS)},
        )
    try:
        loaded = load_manifest(detected, path)
    except QualificationError as exc:
        raise _checked_qualification_error("manifest", path, exc) from exc
    payload = _payload(
        "manifest",
        "valid",
        manifest_subcommand="validate",
        kind=loaded.kind,
        path=str(path),
        schema_version=str(loaded.data["schema_version"]),
        source_sha256=loaded.source_sha256,
    )
    return _EXIT_OK, payload


# ---------------------------------------------------------------------------
# task eligibility
# ---------------------------------------------------------------------------


def run_task_eligible(task_id: str) -> tuple[int, dict[str, Any]]:
    """Evaluate one task against the verified canonical-main checkout."""

    result = evaluate_task_eligibility(task_id)
    exit_code = _EXIT_OK if result["eligible"] else _EXIT_FAIL_CLOSED
    return exit_code, result


# ---------------------------------------------------------------------------
# parser and dispatch
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mstr-qualify",
        description="MSTR preconstruction qualification harness (offline commands only)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    validate_parser = subparsers.add_parser(
        "validate",
        help="self-check schemas/fixtures, or validate explicit JSON files",
        description=(
            "With no arguments, self-check every registered repository schema "
            "and verify the canonical valid/invalid fixture sets. With paths, "
            "validate each JSON file against its auto-detected canonical contract."
        ),
    )
    validate_parser.add_argument(
        "paths", nargs="*", type=Path, help="optional JSON files to validate"
    )

    rights_parser = subparsers.add_parser(
        "rights",
        help="recompute fail-closed primary rights for a candidate config",
    )
    rights_parser.add_argument("candidate_config", type=Path)

    candidate_parser = subparsers.add_parser(
        "candidate",
        help="candidate qualification subcommands (static only in T010)",
    )
    candidate_subparsers = candidate_parser.add_subparsers(dest="candidate_command", required=True)
    static_parser = candidate_subparsers.add_parser(
        "static",
        help="report a static qualification summary without accessing weights",
    )
    static_parser.add_argument("candidate_config", type=Path)

    task_parser = subparsers.add_parser(
        "task",
        help="offline canonical task-gate checks",
    )
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)
    task_eligible_parser = task_subparsers.add_parser(
        "eligible",
        help="evaluate one task against canonical repository-local state",
    )
    task_eligible_parser.add_argument("task_id")

    manifest_parser = subparsers.add_parser(
        "manifest",
        help="manifest subcommands (validate only in T010)",
    )
    manifest_subparsers = manifest_parser.add_subparsers(dest="manifest_command", required=True)
    manifest_validate_parser = manifest_subparsers.add_parser(
        "validate",
        help="validate a task/candidate/benchmark manifest locally",
    )
    manifest_validate_parser.add_argument("manifest", type=Path)
    manifest_validate_parser.add_argument(
        "--kind",
        choices=_MANIFEST_KINDS,
        default=None,
        help="override manifest-kind auto-detection",
    )
    return parser


def _dispatch(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if args.command == "validate":
        return run_validate(args.paths)
    if args.command == "rights":
        return run_rights(args.candidate_config)
    if args.command == "candidate":
        if args.candidate_command == "static":
            return run_candidate_static(args.candidate_config)
        raise QualificationError(
            "unknown candidate subcommand",
            code="cli.subcommand_unknown",
            details={"subcommand": str(args.candidate_command)},
        )
    if args.command == "task":
        if args.task_command == "eligible":
            return run_task_eligible(args.task_id)
        raise QualificationError(
            "unknown task subcommand",
            code="cli.subcommand_unknown",
            details={"subcommand": str(args.task_command)},
        )
    if args.command == "manifest":
        if args.manifest_command == "validate":
            return run_manifest_validate(args.manifest, args.kind)
        raise QualificationError(
            "unknown manifest subcommand",
            code="cli.subcommand_unknown",
            details={"subcommand": str(args.manifest_command)},
        )
    raise QualificationError(
        "unknown command",
        code="cli.command_unknown",
        details={"command": str(getattr(args, "command", None))},
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return _EXIT_OK
    try:
        exit_code, payload = _dispatch(args)
    except _CheckedFailure as failure:
        print(_dump(failure.payload))
        return _EXIT_FAIL_CLOSED
    except QualificationError as exc:
        error_payload = {
            "status": "error",
            "command": getattr(args, "command", None),
            "code": exc.code,
            "message": exc.message,
            "details": dict(exc.details),
        }
        print(_dump(error_payload), file=sys.stderr)
        return _EXIT_ERROR
    print(_dump(payload))
    return exit_code
