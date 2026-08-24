from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from mstr_qualify.errors import ConfigurationError, SchemaValidationError
from mstr_qualify.manifests import (
    load_benchmark_manifest,
    load_candidate_manifest,
    load_manifest,
    load_task_manifest,
)


def write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def candidate() -> dict[str, object]:
    rights = {
        "decision": "pass_permissive",
        "license_name": "Fixture License",
        "terms_urls": ["https://example.invalid/terms"],
        "personal_use": "yes",
        "commercial_use": "yes",
        "modification": "yes",
        "fine_tuning": "yes",
        "quantization": "yes",
        "derivative_redistribution": "yes",
        "account_gate_required": False,
        "clickthrough_gate_required": False,
        "end_user_separate_license_required": False,
        "field_or_scale_restrictions": [],
        "rationale": "fixture",
    }
    return {
        "schema_version": "mstr.candidate.v1",
        "candidate_id": "candidate-fixture",
        "upstream_id": "example/model",
        "upstream_revision": "revision-1",
        "candidate_role": "foundation",
        "status": "discovered",
        "rights": rights,
        "architecture": {
            "family": "fixture",
            "parameter_count_total": 1,
            "parameter_count_active": 1,
            "tokenizer_id": "example/tokenizer",
            "tokenizer_revision": "revision-1",
            "vision_components": [],
            "fim_capability": "unknown",
        },
        "runtime_support_notes": [],
        "quantization_support_notes": [],
        "source_urls": ["https://example.invalid/source"],
    }


def task() -> dict[str, object]:
    return {
        "schema_version": "mstr.task.v1",
        "task_id": "task-fixture",
        "repository": "example/repo",
        "base_revision": "revision-1",
        "task_text": "Fix the fixture.",
        "workspace_scope": ["src/"],
        "required_verifiers": ["pytest"],
        "timeout_seconds": 60,
        "seed": 0,
        "sampling": {},
        "tool_budget": 10,
        "network_policy": "disabled",
        "network_allowlist": [],
        "future_history_policy": "blocked",
        "hidden_artifact_ids": [],
        "benchmark_exclusion_class": None,
        "notes": [],
    }


def benchmark() -> dict[str, object]:
    return {
        "schema_version": "mstr.benchmark.v1",
        "benchmark_id": "fixture",
        "purpose": "qualification",
        "surface": "static",
        "task_ids": ["t1"],
        "candidate_ids": ["c1"],
        "seeds": [0, 1],
        "sampling": {"temperature": 0},
        "timeout_seconds": 60,
        "verifier_policy": {"required": True},
        "tools": [],
        "network_policy": "disabled",
        "cache_requirements": {"state": "process_cold"},
        "comparison_policy": {"same_manifest": True},
        "source_commit": "abc123",
    }


def test_candidate_validates_against_registered_schema(tmp_path: Path) -> None:
    loaded = load_candidate_manifest(write(tmp_path / "c.json", candidate()))
    assert loaded.kind == "candidate"
    assert loaded.data["candidate_id"] == "candidate-fixture"


def test_task_validates_against_registered_schema(tmp_path: Path) -> None:
    loaded = load_task_manifest(write(tmp_path / "t.json", task()))
    assert loaded.kind == "task"
    assert loaded.data["task_id"] == "task-fixture"


def test_candidate_schema_failure_propagates(tmp_path: Path) -> None:
    value = candidate()
    value.pop("upstream_revision")
    with pytest.raises(SchemaValidationError):
        load_candidate_manifest(write(tmp_path / "bad.json", value))


def test_source_sha256_is_exact_file_identity(tmp_path: Path) -> None:
    path = write(tmp_path / "b.json", benchmark())
    loaded = load_benchmark_manifest(path)
    assert loaded.source_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()


def test_benchmark_validates_and_dispatches(tmp_path: Path) -> None:
    path = write(tmp_path / "b.json", benchmark())
    assert load_benchmark_manifest(path).kind == "benchmark"
    assert load_manifest("benchmark", path).data["benchmark_id"] == "fixture"


@pytest.mark.parametrize("field", sorted(benchmark()))
def test_benchmark_rejects_missing_required_fields(tmp_path: Path, field: str) -> None:
    value = benchmark()
    value.pop(field)
    with pytest.raises(ConfigurationError):
        load_benchmark_manifest(write(tmp_path / f"{field}.json", value))


def test_benchmark_rejects_unknown_fields(tmp_path: Path) -> None:
    value = benchmark()
    value["surprise"] = True
    with pytest.raises(ConfigurationError, match="manifest.benchmark_unknown"):
        load_benchmark_manifest(write(tmp_path / "b.json", value))


@pytest.mark.parametrize("field", ["task_ids", "candidate_ids"])
def test_benchmark_rejects_duplicate_identity_lists(tmp_path: Path, field: str) -> None:
    value = benchmark()
    value[field] = ["x", "x"]
    with pytest.raises(ConfigurationError, match="manifest.benchmark_duplicate"):
        load_benchmark_manifest(write(tmp_path / "b.json", value))


@pytest.mark.parametrize("seeds", [[], [True], [1, 1], ["1"]])
def test_benchmark_rejects_invalid_seeds(tmp_path: Path, seeds: object) -> None:
    value = benchmark()
    value["seeds"] = seeds
    with pytest.raises(ConfigurationError, match="manifest.benchmark_seeds"):
        load_benchmark_manifest(write(tmp_path / "b.json", value))


@pytest.mark.parametrize("timeout", [0, -1, True, 1.5])
def test_benchmark_rejects_invalid_timeout(tmp_path: Path, timeout: object) -> None:
    value = benchmark()
    value["timeout_seconds"] = timeout
    with pytest.raises(ConfigurationError, match="manifest.benchmark_timeout"):
        load_benchmark_manifest(write(tmp_path / "b.json", value))


def test_benchmark_rejects_network_policy(tmp_path: Path) -> None:
    value = benchmark()
    value["network_policy"] = "internet"
    with pytest.raises(ConfigurationError, match="manifest.benchmark_network_policy"):
        load_benchmark_manifest(write(tmp_path / "b.json", value))


def test_non_json_extension_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="manifest.extension"):
        load_benchmark_manifest(path)


def test_invalid_json_and_root_fail_closed(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="manifest.json_invalid"):
        load_benchmark_manifest(bad)
    with pytest.raises(ConfigurationError, match="manifest.root_type"):
        load_benchmark_manifest(write(tmp_path / "list.json", []))


def test_unknown_kind_fails_closed(tmp_path: Path) -> None:
    path = write(tmp_path / "x.json", benchmark())
    with pytest.raises(ConfigurationError, match="manifest.kind"):
        load_manifest("unknown", path)
