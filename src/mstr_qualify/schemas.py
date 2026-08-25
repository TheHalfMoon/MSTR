"""Strict local JSON Schema loading and validation for MSTR qualification records.

T004 deliberately supports only a fixed set of repository-local schemas. Remote
references are rejected before a validator is constructed so schema validation
cannot become an implicit network boundary.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from .errors import SchemaValidationError

SCHEMA_FILES: Mapping[str, str] = {
    "candidate-record": "candidate-record.schema.json",
    "task-manifest": "task-manifest.schema.json",
    "run-evidence": "run-evidence.schema.json",
    "interaction-contract": "interaction-contract.schema.json",
}

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_DIR = _REPOSITORY_ROOT / "schemas"


def _walk_json(value: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def _reject_external_refs(schema: Mapping[str, Any]) -> None:
    for key, value in _walk_json(schema):
        if key != "$ref":
            continue
        if not isinstance(value, str):
            raise SchemaValidationError(
                "schema $ref values must be strings", code="schema.ref_type"
            )
        if not value.startswith("#"):
            raise SchemaValidationError(
                "external schema reference is prohibited",
                code="schema.external_ref",
                details={"ref": value},
            )


def load_schema(name: str, *, schema_dir: Path | None = None) -> dict[str, Any]:
    """Load and self-check one registered repository-local schema."""

    try:
        filename = SCHEMA_FILES[name]
    except KeyError as exc:
        allowed = ", ".join(sorted(SCHEMA_FILES))
        raise SchemaValidationError(
            "unknown schema",
            code="schema.unknown",
            details={"name": name, "allowed": allowed},
        ) from exc

    path = (schema_dir or DEFAULT_SCHEMA_DIR) / filename
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SchemaValidationError(
            "unable to read schema",
            code="schema.read",
            details={"name": name, "path": str(path)},
        ) from exc

    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(
            "schema is not valid JSON",
            code="schema.json",
            details={"name": name, "reason": exc.msg},
        ) from exc

    if not isinstance(schema, dict):
        raise SchemaValidationError(
            "schema must contain a JSON object",
            code="schema.root_type",
            details={"name": name},
        )

    _reject_external_refs(schema)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise SchemaValidationError(
            "schema is not valid Draft 2020-12 JSON Schema",
            code="schema.meta",
            details={"name": name, "reason": exc.message},
        ) from exc
    return schema


def _format_validation_error(error: ValidationError) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return f"{path}: {error.message}"


def validation_errors(
    name: str,
    instance: Any,
    *,
    schema_dir: Path | None = None,
) -> tuple[str, ...]:
    """Return deterministic, human-readable validation errors."""

    schema = load_schema(name, schema_dir=schema_dir)
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            tuple(str(part) for part in error.absolute_schema_path),
            error.message,
        ),
    )
    return tuple(_format_validation_error(error) for error in errors)


def validate_instance(
    name: str,
    instance: Any,
    *,
    schema_dir: Path | None = None,
) -> None:
    """Validate an already-decoded JSON value and fail closed on any violation."""

    errors = validation_errors(name, instance, schema_dir=schema_dir)
    if errors:
        joined = "\n".join(f"- {message}" for message in errors)
        raise SchemaValidationError(
            f"{name} validation failed:\n{joined}",
            code="schema.instance_invalid",
            details={"schema": name},
        )


def validate_json_file(
    name: str,
    path: Path,
    *,
    schema_dir: Path | None = None,
) -> None:
    """Load UTF-8 JSON from *path* and validate it against a registered schema."""

    try:
        instance = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SchemaValidationError(
            "unable to read JSON instance",
            code="schema.instance_read",
            details={"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(
            "instance is not valid JSON",
            code="schema.instance_json",
            details={"path": str(path), "reason": exc.msg},
        ) from exc
    validate_instance(name, instance, schema_dir=schema_dir)
