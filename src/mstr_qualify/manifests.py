"""Local-only manifest loading and validation for MSTR qualification inputs."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .errors import ConfigurationError
from .ids import sha256_file
from .schemas import validate_instance

ManifestKind = Literal["candidate", "task", "benchmark"]

_BENCHMARK_REQUIRED = frozenset(
    {
        "schema_version",
        "benchmark_id",
        "purpose",
        "surface",
        "task_ids",
        "candidate_ids",
        "seeds",
        "sampling",
        "timeout_seconds",
        "verifier_policy",
        "tools",
        "network_policy",
        "cache_requirements",
        "comparison_policy",
        "source_commit",
    }
)
_BENCHMARK_OPTIONAL = frozenset({"notes"})
_BENCHMARK_FIELDS = _BENCHMARK_REQUIRED | _BENCHMARK_OPTIONAL
_NETWORK_POLICIES = frozenset({"disabled", "loopback_only", "explicit_allowlist"})


@dataclass(frozen=True, slots=True)
class LoadedManifest:
    kind: ManifestKind
    path: Path
    source_sha256: str
    data: dict[str, Any]


def _fail(message: str, code: str, **details: object) -> ConfigurationError:
    return ConfigurationError(message, code=code, details=details)


def _read_json_object(path: Path) -> dict[str, Any]:
    if path.suffix.lower() != ".json":
        raise _fail("manifest path must end in .json", "manifest.extension", path=str(path))
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _fail("unable to read manifest", "manifest.read", path=str(path)) from exc
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _fail(
            "manifest is not valid JSON",
            "manifest.json_invalid",
            path=str(path),
            line=exc.lineno,
            column=exc.colno,
        ) from exc
    if not isinstance(decoded, dict):
        raise _fail("manifest root must be a JSON object", "manifest.root_type", path=str(path))
    return decoded


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise _fail(
            "benchmark manifest field must be a non-empty trimmed string",
            "manifest.benchmark_string",
            field=field,
        )
    return value


def _unique_strings(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise _fail(
            "benchmark manifest field must be a list of strings",
            "manifest.benchmark_string_list",
            field=field,
        )
    result: list[str] = []
    for item in value:
        result.append(_nonempty_string(item, field))
    if len(set(result)) != len(result):
        raise _fail(
            "benchmark manifest list values must be unique",
            "manifest.benchmark_duplicate",
            field=field,
        )
    return result


def _validate_mapping(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise _fail(
            "benchmark manifest field must be an object",
            "manifest.benchmark_object",
            field=field,
        )


def _validate_benchmark_manifest(data: Mapping[str, Any]) -> None:
    keys = set(data)
    missing = sorted(_BENCHMARK_REQUIRED - keys)
    if missing:
        raise _fail(
            "benchmark manifest is missing required fields",
            "manifest.benchmark_missing",
            fields=",".join(missing),
        )
    unknown = sorted(keys - _BENCHMARK_FIELDS)
    if unknown:
        raise _fail(
            "benchmark manifest contains unknown fields",
            "manifest.benchmark_unknown",
            fields=",".join(unknown),
        )
    if data["schema_version"] != "mstr.benchmark.v1":
        raise _fail(
            "unsupported benchmark manifest schema_version",
            "manifest.benchmark_schema_version",
            value=data["schema_version"],
        )

    for field in ("benchmark_id", "purpose", "surface", "source_commit"):
        _nonempty_string(data[field], field)

    _unique_strings(data["task_ids"], "task_ids")
    _unique_strings(data["candidate_ids"], "candidate_ids")
    _unique_strings(data["tools"], "tools", allow_empty=True)
    if "notes" in data:
        _unique_strings(data["notes"], "notes", allow_empty=True)

    seeds = data["seeds"]
    if (
        not isinstance(seeds, list)
        or not seeds
        or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise _fail(
            "seeds must be a non-empty unique list of integers",
            "manifest.benchmark_seeds",
        )

    timeout = data["timeout_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
        raise _fail(
            "timeout_seconds must be a positive integer",
            "manifest.benchmark_timeout",
        )

    for field in ("sampling", "verifier_policy", "cache_requirements", "comparison_policy"):
        _validate_mapping(data[field], field)

    network_policy = data["network_policy"]
    if network_policy not in _NETWORK_POLICIES:
        raise _fail(
            "unsupported benchmark network policy",
            "manifest.benchmark_network_policy",
            value=network_policy,
        )


def _load(kind: ManifestKind, path: Path) -> LoadedManifest:
    data = _read_json_object(path)
    if kind == "candidate":
        validate_instance("candidate-record", data)
    elif kind == "task":
        validate_instance("task-manifest", data)
    elif kind == "benchmark":
        _validate_benchmark_manifest(data)
    else:  # pragma: no cover - protected by typed public dispatch
        raise _fail("unsupported manifest kind", "manifest.kind", kind=kind)
    return LoadedManifest(
        kind=kind,
        path=path,
        source_sha256=sha256_file(path),
        data=dict(data),
    )


def load_candidate_manifest(path: Path) -> LoadedManifest:
    return _load("candidate", path)


def load_task_manifest(path: Path) -> LoadedManifest:
    return _load("task", path)


def load_benchmark_manifest(path: Path) -> LoadedManifest:
    return _load("benchmark", path)


def load_manifest(kind: str, path: Path) -> LoadedManifest:
    if kind == "candidate":
        return load_candidate_manifest(path)
    if kind == "task":
        return load_task_manifest(path)
    if kind == "benchmark":
        return load_benchmark_manifest(path)
    raise _fail(
        "unsupported manifest kind",
        "manifest.kind",
        kind=kind,
        allowed="benchmark,candidate,task",
    )
