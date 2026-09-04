"""Fail-closed B011 model-weight acquisition planning and report verification.

This module does not perform network I/O. It binds acquisition to the exact
canonical B010 manifest and B011 Founder authority, derives the permitted HTTPS
GET plan, and validates durable reports emitted by approved ephemeral runners.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .errors import QualificationError

B010_SHA256 = "4c2fd1469cdcf728063ab8f5b6a603191ffdc9e1a4d4c2d794abd2a24950c3ef"
AUTHORITY_ID = "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
AUTHORITY_DECISION = "FOUNDER_B011_MODEL_WEIGHT_ACCESS_DECISION=AUTHORIZE_EXACT_B010_ENVELOPE"
EXPECTED_CANDIDATES = ("mellum-4b", "qwen3.5-0.8b-control")
RESOLVE_HOST = "huggingface.co"
PROHIBITED_TRUE_SCOPE_FLAGS = (
    "paid_compute",
    "paid_model_api",
    "gated_terms_acceptance",
    "quantization_execution",
    "weight_changing_training",
    "large_dataset_ingestion",
    "production_release",
    "git_model_binaries",
)


@dataclass(frozen=True)
class B011PlannedFile:
    candidate_id: str
    model_repo: str
    model_revision: str
    filename: str
    url: str
    expected_sha256: str | None
    expected_size_bytes: int
    allowed_hosts: tuple[str, ...]


def _fail(message: str, code: str, **details: Any) -> None:
    raise QualificationError(message, code=code, details=details or None)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_b011_inputs(
    b010_path: Path,
    authority_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    b010_bytes = b010_path.read_bytes()
    if _sha256(b010_bytes) != B010_SHA256:
        _fail(
            "B010 manifest bytes do not match the Founder-authorized digest",
            "b011.b010_digest_mismatch",
            expected=B010_SHA256,
            actual=_sha256(b010_bytes),
        )
    b010 = json.loads(b010_bytes)
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    validate_b011_inputs(b010, authority)
    return b010, authority


def validate_b011_inputs(b010: dict[str, Any], authority: dict[str, Any]) -> None:
    if b010.get("schema_version") != "mstr.b010-new-candidate-weight-access.v1":
        _fail("unexpected B010 schema", "b011.b010_schema")
    if authority.get("authority_id") != AUTHORITY_ID or authority.get("task_id") != "B011":
        _fail("wrong B011 authority identity", "b011.authority_identity")
    if authority.get("status") != "AUTHORIZED_CANONICAL":
        _fail("B011 authority is not canonical", "b011.authority_status")

    scope = authority.get("scope")
    if not isinstance(scope, dict):
        _fail("B011 authority scope is missing", "b011.authority_scope")
    bound = scope.get("b010_manifest")
    if not isinstance(bound, dict) or bound.get("sha256") != B010_SHA256:
        _fail("B011 authority does not bind exact B010 digest", "b011.authority_b010_binding")
    if scope.get("decision") != AUTHORITY_DECISION:
        _fail("B011 Founder decision does not match", "b011.authority_decision")

    decision = b010.get("decision")
    if not isinstance(decision, dict):
        _fail("B010 decision missing", "b011.b010_decision")
    candidates = decision.get("new_weight_access_required_candidates")
    if tuple(candidates or ()) != EXPECTED_CANDIDATES:
        _fail("B010 access-required candidate set drifted", "b011.candidate_set", actual=candidates)
    if tuple(scope.get("candidate_ids") or ()) != EXPECTED_CANDIDATES:
        _fail("authority candidate set drifted", "b011.authority_candidate_set")

    envelopes = b010.get("candidate_access_envelopes")
    auth_envelopes = scope.get("candidate_access_envelopes")
    if not isinstance(envelopes, list) or envelopes != auth_envelopes:
        _fail("B010 and authority access envelopes differ", "b011.envelope_mismatch")
    if tuple(e.get("candidate_id") for e in envelopes) != EXPECTED_CANDIDATES:
        _fail("B010 envelope order/set drifted", "b011.envelope_candidate_set")

    ceiling = authority.get("cost_resource_ceiling", {}).get("limits", [])
    byte_limits = [x.get("max") for x in ceiling if x.get("resource") == "required_download_bytes"]
    cost_limits = [x.get("max") for x in ceiling if x.get("resource") == "cost"]
    expected_bytes = sum(int(e["expected_required_download_bytes"]) for e in envelopes)
    if byte_limits != [expected_bytes] or cost_limits != [0.0]:
        _fail("authority resource ceiling drifted", "b011.resource_ceiling")

    for key in PROHIBITED_TRUE_SCOPE_FLAGS:
        if scope.get(key) is not False:
            _fail("B011 authority boundary widened", "b011.authority_boundary", field=key)
    if scope.get("founder_machine_large_artifacts") != 0:
        _fail("Founder machine artifact ceiling widened", "b011.founder_machine_boundary")

    for envelope in envelopes:
        hosts = envelope.get("network_hosts")
        if not isinstance(hosts, list) or RESOLVE_HOST not in hosts or len(hosts) != len(set(hosts)):
            _fail("invalid B011 host allowlist", "b011.host_allowlist", candidate=envelope.get("candidate_id"))
        if envelope.get("network_policy") != "HTTPS_GET_ONLY_AFTER_B011_EXACT_FOUNDER_AUTHORIZATION; ABORT_ON_AUTH_GATING_PAYMENT_OR_UNLISTED_REDIRECT":
            _fail("B011 network policy drifted", "b011.network_policy")
        if envelope.get("usd_ceiling") != 0.0 or envelope.get("expected_usd") != 0.0:
            _fail("B011 zero-USD boundary drifted", "b011.cost_boundary")
        if envelope.get("executor") != "B011_APPROVED_EPHEMERAL_CLOUD_RUNNER_AFTER_EXACT_FOUNDER_AUTHORIZATION":
            _fail("B011 executor boundary drifted", "b011.executor")
        if "NEVER_GIT; NEVER_FOUNDER_MACHINE" not in str(envelope.get("storage")):
            _fail("B011 storage boundary drifted", "b011.storage")
        rights = envelope.get("rights_status")
        if not isinstance(rights, dict) or rights.get("decision") != "pass_permissive":
            _fail("B011 rights gate is not passing", "b011.rights")
        if any(rights.get(k) is not False for k in ("account_required", "clickthrough_required", "gated_terms_acceptance_required")):
            _fail("B011 rights require interaction or gated acceptance", "b011.rights_gated")


def build_b011_plan(b010: dict[str, Any], authority: dict[str, Any]) -> tuple[B011PlannedFile, ...]:
    validate_b011_inputs(b010, authority)
    plan: list[B011PlannedFile] = []
    for envelope in b010["candidate_access_envelopes"]:
        candidate_id = str(envelope["candidate_id"])
        repo = str(envelope["upstream_id"])
        revision = str(envelope["exact_revision"])
        hosts = tuple(str(h) for h in envelope["network_hosts"])
        required = envelope.get("required_files")
        if not isinstance(required, list) or not required:
            _fail("B011 candidate has no required files", "b011.required_files", candidate=candidate_id)
        total = 0
        for entry in required:
            filename = str(entry["path"])
            size = int(entry["size_bytes"])
            sha = entry.get("sha256")
            if entry.get("artifact_class") == "MODEL_WEIGHT" and not isinstance(sha, str):
                _fail("B011 weight lacks pinned SHA-256", "b011.weight_hash", candidate=candidate_id, file=filename)
            url = f"https://{RESOLVE_HOST}/{repo}/resolve/{revision}/{filename}"
            if urlparse(url).hostname not in hosts:
                _fail("initial resolve URL is outside allowlist", "b011.resolve_host")
            plan.append(
                B011PlannedFile(
                    candidate_id=candidate_id,
                    model_repo=repo,
                    model_revision=revision,
                    filename=filename,
                    url=url,
                    expected_sha256=sha if isinstance(sha, str) else None,
                    expected_size_bytes=size,
                    allowed_hosts=hosts,
                )
            )
            total += size
        if total != int(envelope["expected_required_download_bytes"]):
            _fail("B011 candidate byte total drifted", "b011.candidate_bytes", candidate=candidate_id)
    return tuple(plan)


def assert_allowed_redirect(url: str, allowed_hosts: tuple[str, ...]) -> str:
    host = urlparse(url).hostname or ""
    if host not in allowed_hosts:
        _fail("redirect host is outside the frozen B011 allowlist", "b011.redirect_host", host=host)
    return host


def verify_b011_report(report: dict[str, Any], plan: tuple[B011PlannedFile, ...]) -> None:
    if report.get("schema_version") != "mstr.b011-acquisition-report.v1":
        _fail("unexpected B011 report schema", "b011.report_schema")
    if report.get("b010_sha256") != B010_SHA256 or report.get("authority_id") != AUTHORITY_ID:
        _fail("B011 report is not bound to canonical authority", "b011.report_binding")
    candidate = report.get("candidate_id")
    expected = [p for p in plan if p.candidate_id == candidate]
    if not expected:
        _fail("B011 report candidate is outside plan", "b011.report_candidate")
    rows = report.get("files")
    if not isinstance(rows, list) or len(rows) != len(expected):
        _fail("B011 report file count mismatch", "b011.report_file_count")
    by_name = {str(r.get("filename")): r for r in rows}
    if len(by_name) != len(rows):
        _fail("B011 report contains duplicate files", "b011.report_duplicate")
    for planned in expected:
        row = by_name.get(planned.filename)
        if row is None or row.get("status") != "ACQUIRED_VERIFIED":
            _fail("B011 report contains an unverified file", "b011.report_unverified", file=planned.filename)
        if row.get("size_bytes") != planned.expected_size_bytes:
            _fail("B011 report size mismatch", "b011.report_size", file=planned.filename)
        if planned.expected_sha256 is not None and row.get("sha256") != planned.expected_sha256:
            _fail("B011 report hash mismatch", "b011.report_hash", file=planned.filename)
        if row.get("model_repo") != planned.model_repo or row.get("model_revision") != planned.model_revision:
            _fail("B011 report model identity mismatch", "b011.report_identity", file=planned.filename)
        observed = row.get("redirect_hosts")
        if not isinstance(observed, list):
            _fail("B011 report redirect evidence missing", "b011.report_redirects", file=planned.filename)
        for host in observed:
            if host not in planned.allowed_hosts:
                _fail("B011 report observed unlisted redirect", "b011.report_redirect_host", host=host)
    if report.get("actual_download_bytes") != sum(p.expected_size_bytes for p in expected):
        _fail("B011 report aggregate bytes mismatch", "b011.report_bytes")
