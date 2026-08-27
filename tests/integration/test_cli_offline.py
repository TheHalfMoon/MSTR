"""T010 integration tests: offline CLI commands without weights or network.

These tests exercise `mstr_qualify.cli.main` end-to-end and enforce:

- deterministic JSON output on stdout;
- the documented exit-code contract (0 pass / 1 checked fail-closed / 2 error);
- fail-closed rights recomputation through the T006 evaluator;
- local-only behavior (socket creation is blocked during every command).
"""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

import pytest

from mstr_qualify.__main__ import main
from mstr_qualify.ids import sha256_file


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def parse_stdout(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    return json.loads(capsys.readouterr().out)


def candidate_config() -> dict[str, Any]:
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
        "rationale": "fixture evidence supports all required rights",
    }
    return {
        "schema_version": "mstr.candidate.v1",
        "candidate_id": "cli-fixture-candidate",
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


def task_manifest() -> dict[str, Any]:
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


def benchmark_manifest() -> dict[str, Any]:
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


@pytest.fixture(autouse=True)
def block_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any test that attempts outbound network access."""

    def _blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("offline CLI attempted to open a network socket")

    monkeypatch.setattr(socket, "socket", _blocked)


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def test_validate_self_checks_schemas_and_fixtures(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate"]) == 0
    payload = parse_stdout(capsys)
    assert payload["command"] == "validate"
    assert payload["status"] == "pass"
    assert payload["schemas_checked"] == [
        "candidate-record",
        "interaction-contract",
        "mstr-loop-contract-v0",
        "mstr-run-event-v0",
        "mstr-task-eligibility-v0",
        "mstr-task-node-v0",
        "run-evidence",
        "storage-amendment",
        "task-manifest",
        "weight-access-manifest",
    ]
    assert payload["valid_fixtures_passed"] >= 5
    assert payload["invalid_fixtures_rejected"] >= 5


def test_validate_is_deterministic_across_runs(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate"]) == 0
    first_out = capsys.readouterr().out
    assert main(["validate"]) == 0
    second_out = capsys.readouterr().out
    assert second_out == first_out


def test_validate_explicit_candidate_file_passes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_json(tmp_path / "candidate.json", candidate_config())
    assert main(["validate", str(path)]) == 0
    payload = parse_stdout(capsys)
    assert payload["status"] == "pass"
    assert payload["files"][0]["schema_version"] == "mstr.candidate.v1"


def test_validate_explicit_invalid_file_fails_closed(tmp_path: Path, capsys: Any) -> None:
    bad = candidate_config()
    bad["candidate_role"] = "not-a-role"
    path = write_json(tmp_path / "bad.json", bad)
    assert main(["validate", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert payload["status"] == "fail"
    assert payload["files"][0]["code"] == "schema.instance_invalid"


def test_validate_file_without_schema_version_fails_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_json(tmp_path / "anon.json", {"anything": True})
    assert main(["validate", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert payload["files"][0]["code"] == "cli.schema_version_missing"


def test_validate_missing_file_is_invocation_error(tmp_path: Path, capsys: Any) -> None:
    missing = tmp_path / "missing.json"
    assert main(["validate", str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    error_payload = json.loads(captured.err)
    assert error_payload["status"] == "error"
    assert error_payload["code"] == "cli.input_missing"


# ---------------------------------------------------------------------------
# rights
# ---------------------------------------------------------------------------


def test_rights_passes_permissive_candidate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_json(tmp_path / "candidate.json", candidate_config())
    assert main(["rights", str(path)]) == 0
    payload = parse_stdout(capsys)
    assert payload["command"] == "rights"
    assert payload["status"] == "pass"
    assert payload["computed_decision"] == "pass_permissive"
    assert payload["eligible_for_primary"] is True
    assert payload["reason_codes"] == []


def test_rights_declared_decision_cannot_bypass_recomputation(tmp_path: Path, capsys: Any) -> None:
    config = candidate_config()
    config["rights"]["commercial_use"] = "no"
    path = write_json(tmp_path / "candidate.json", config)
    assert main(["rights", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert payload["status"] == "fail"
    assert payload["eligible_for_primary"] is False
    assert "cli-fixture-candidate:commercial_use_denied" in payload["reason_codes"]
    # The T006 gate recomputes from facts; a permissive-looking declaration
    # must never mask an explicit denial.
    assert payload["computed_decision"] == "fail"


def test_rights_unknown_answer_fails_closed(tmp_path: Path, capsys: Any) -> None:
    config = candidate_config()
    config["rights"]["quantization"] = "unknown"
    path = write_json(tmp_path / "candidate.json", config)
    assert main(["rights", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert "cli-fixture-candidate:quantization_unknown" in payload["reason_codes"]


# ---------------------------------------------------------------------------
# candidate static
# ---------------------------------------------------------------------------


def test_candidate_static_passes_and_binds_source_identity(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_json(tmp_path / "candidate.json", candidate_config())
    expected_sha256 = sha256_file(path)

    assert main(["candidate", "static", str(path)]) == 0
    first_out = capsys.readouterr().out
    first_payload = json.loads(first_out)

    assert first_payload["command"] == "candidate"
    assert first_payload["candidate_subcommand"] == "static"
    assert first_payload["status"] == "static_qualified"
    assert first_payload["weights_accessed"] is False
    assert first_payload["source_sha256"] == expected_sha256
    assert first_payload["static_record_id"]

    # Deterministic identity binding: same bytes produce identical output.
    assert main(["candidate", "static", str(path)]) == 0
    assert capsys.readouterr().out == first_out


def test_candidate_static_fails_closed_on_incompatible_rights(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = candidate_config()
    config["rights"]["decision"] = "pass_conditional"
    config["rights"]["end_user_separate_license_required"] = True
    path = write_json(tmp_path / "candidate.json", config)
    assert main(["candidate", "static", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert payload["status"] == "static_failed"
    assert "cli-fixture-candidate:end_user_separate_license_required" in payload["reason_codes"]


def test_candidate_static_reports_schema_invalid_input_as_checked_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = candidate_config()
    del config["architecture"]["tokenizer_id"]
    path = write_json(tmp_path / "candidate.json", config)
    assert main(["candidate", "static", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert payload["status"] == "fail"
    assert payload["code"] == "schema.instance_invalid"


# ---------------------------------------------------------------------------
# manifest validate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "builder",
    [candidate_config, task_manifest, benchmark_manifest],
)
def test_manifest_validate_auto_detects_all_kinds(
    tmp_path: Path, builder: Any, capsys: Any
) -> None:
    expected_kind = {
        candidate_config: "candidate",
        task_manifest: "task",
        benchmark_manifest: "benchmark",
    }[builder]
    path = write_json(tmp_path / "manifest.json", builder())
    assert main(["manifest", "validate", str(path)]) == 0
    payload = parse_stdout(capsys)
    assert payload["kind"] == expected_kind
    assert payload["status"] == "valid"
    assert payload["source_sha256"] == sha256_file(path)


def test_manifest_validate_explicit_kind_override(tmp_path: Path, capsys: Any) -> None:
    path = write_json(tmp_path / "task.json", task_manifest())
    assert main(["manifest", "validate", str(path), "--kind", "task"]) == 0
    payload = parse_stdout(capsys)
    assert payload["kind"] == "task"


def test_manifest_validate_undetectable_kind_is_invocation_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_json(tmp_path / "run.json", {"schema_version": "mstr.run.v1"})
    assert main(["manifest", "validate", str(path)]) == 2
    error_payload = json.loads(capsys.readouterr().err)
    assert error_payload["code"] == "cli.manifest_kind_unknown"


def test_manifest_validate_invalid_content_fails_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = benchmark_manifest()
    bad["task_ids"] = ["t1", "t1"]
    path = write_json(tmp_path / "benchmark.json", bad)
    assert main(["manifest", "validate", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert payload["status"] == "fail"
    assert payload["code"] == "manifest.benchmark_duplicate"


def test_manifest_validate_missing_file_is_invocation_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.json"
    assert main(["manifest", "validate", str(missing)]) == 2
    error_payload = json.loads(capsys.readouterr().err)
    assert error_payload["code"] == "cli.input_missing"


# ---------------------------------------------------------------------------
# general CLI discipline
# ---------------------------------------------------------------------------


def test_no_arguments_prints_help_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    for family in ("validate", "rights", "candidate", "manifest"):
        assert family in out


def test_output_is_deterministic_sorted_json(tmp_path: Path, capsys: Any) -> None:
    path = write_json(tmp_path / "candidate.json", candidate_config())
    assert main(["rights", str(path)]) == 0
    first_out = capsys.readouterr().out
    assert main(["rights", str(path)]) == 0
    second_out = capsys.readouterr().out
    assert second_out == first_out
    rendered = json.loads(first_out)
    assert list(rendered) == sorted(rendered)
