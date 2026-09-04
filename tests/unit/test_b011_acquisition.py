from __future__ import annotations

import copy
from pathlib import Path

import pytest

from mstr_qualify.b011_acquisition import (
    B010_SHA256,
    EXPECTED_CANDIDATES,
    assert_allowed_redirect,
    build_b011_plan,
    load_b011_inputs,
    verify_b011_report,
)
from mstr_qualify.errors import QualificationError

ROOT = Path(__file__).resolve().parents[2]
B010 = ROOT / "artifacts/manifests/B010-new-candidate-weight-access.json"
AUTHORITY = ROOT / "artifacts/authorities/B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED.json"


def test_canonical_b011_plan_is_exact_and_bounded() -> None:
    b010, authority = load_b011_inputs(B010, AUTHORITY)
    plan = build_b011_plan(b010, authority)
    assert tuple(dict.fromkeys(p.candidate_id for p in plan)) == EXPECTED_CANDIDATES
    assert len(plan) == 19
    assert sum(p.expected_size_bytes for p in plan) == 9_817_996_174
    assert all(p.url.startswith("https://huggingface.co/") for p in plan)
    assert all("huggingface.co" in p.allowed_hosts for p in plan)
    weight_files = [p for p in plan if p.filename.endswith(".safetensors")]
    assert len(weight_files) == 3
    assert all(p.expected_sha256 is not None for p in weight_files)


def test_b010_authority_digest_is_exact() -> None:
    import hashlib

    assert hashlib.sha256(B010.read_bytes()).hexdigest() == B010_SHA256
    load_b011_inputs(B010, AUTHORITY)


def test_unlisted_redirect_fails_closed() -> None:
    with pytest.raises(QualificationError) as exc:
        assert_allowed_redirect("https://evil.example/model", ("huggingface.co",))
    assert exc.value.code == "b011.redirect_host"


def test_authority_boundary_widening_fails_closed() -> None:
    b010, authority = load_b011_inputs(B010, AUTHORITY)
    widened = copy.deepcopy(authority)
    widened["scope"]["quantization_execution"] = True
    with pytest.raises(QualificationError) as exc:
        build_b011_plan(b010, widened)
    assert exc.value.code == "b011.authority_boundary"


def test_envelope_drift_fails_closed() -> None:
    b010, authority = load_b011_inputs(B010, AUTHORITY)
    drifted = copy.deepcopy(authority)
    drifted["scope"]["candidate_access_envelopes"][0]["network_hosts"].append("example.com")
    with pytest.raises(QualificationError) as exc:
        build_b011_plan(b010, drifted)
    assert exc.value.code == "b011.envelope_mismatch"


def test_verified_report_must_match_exact_plan() -> None:
    b010, authority = load_b011_inputs(B010, AUTHORITY)
    plan = build_b011_plan(b010, authority)
    candidate = EXPECTED_CANDIDATES[1]
    expected = [p for p in plan if p.candidate_id == candidate]
    report = {
        "schema_version": "mstr.b011-acquisition-report.v1",
        "task_id": "MSTR-000B / B011",
        "authority_id": "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED",
        "b010_sha256": B010_SHA256,
        "candidate_id": candidate,
        "actual_download_bytes": sum(p.expected_size_bytes for p in expected),
        "files": [
            {
                "candidate_id": p.candidate_id,
                "filename": p.filename,
                "status": "ACQUIRED_VERIFIED",
                "sha256": p.expected_sha256 or ("0" * 64),
                "size_bytes": p.expected_size_bytes,
                "model_repo": p.model_repo,
                "model_revision": p.model_revision,
                "redirect_hosts": ["huggingface.co"],
            }
            for p in expected
        ],
    }
    verify_b011_report(report, plan)
    report["files"][0]["redirect_hosts"] = ["evil.example"]
    with pytest.raises(QualificationError) as exc:
        verify_b011_report(report, plan)
    assert exc.value.code == "b011.report_redirect_host"
