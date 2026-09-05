from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = (
    ROOT / "artifacts/authorities/T031_FOUNDER_AUTHORITY_FOR_LOCAL_MEASUREMENT_REGENERATION.json"
)
ENVELOPE = ROOT / "artifacts/manifests/T031-local-measurement-execution-envelope.json"


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_t031_authority_binds_exact_founder_decision_and_eight_t029_candidates() -> None:
    authority = _load(AUTHORITY)
    scope = authority["scope"]
    assert isinstance(scope, dict)
    assert authority["authority_id"] == "T031_FOUNDER_AUTHORITY_FOR_LOCAL_MEASUREMENT_REGENERATION"
    assert authority["task_id"] == "T031"
    assert authority["status"] == "AUTHORIZED_CANONICAL"
    assert (
        scope["decision"]
        == "FOUNDER_T031_LOCAL_MEASUREMENT_DECISION=AUTHORIZE_EXACT_T029_CANDIDATES"
    )
    assert scope["decision_surface"] == {"issue": 167, "comment_id": 5553875809}
    assert scope["candidate_ids"] == [
        "granite-4.1-3b",
        "ministral-3-3b",
        "qwen2.5-coder-1.5b",
        "qwen3-4b",
        "qwen3.5-2b",
        "qwen3.5-4b",
        "smollm3-3b",
        "yi-coder-1.5b",
    ]
    assert scope["b010_b012_candidates"] is False
    assert scope["t032_execution"] is False
    assert scope["t033_execution"] is False
    assert scope["t034_admission_decision"] is False
    assert scope["training"] is False
    assert scope["weight_changing_training"] is False


def test_t031_execution_envelope_freezes_identity_but_dispatch_remains_fail_closed() -> None:
    authority = _load(AUTHORITY)
    envelope = _load(ENVELOPE)
    scope = authority["scope"]
    assert isinstance(scope, dict)
    binding = scope["bounded_execution_envelope"]
    assert isinstance(binding, dict)
    assert binding["sha256"] == _sha(ENVELOPE)
    assert envelope["measurement_contract"]["contexts"] == [4096, 8192, 16384]  # type: ignore[index]
    assert envelope["q4_identity"]["llama_cpp_commit"] == "fc35562ba46fbbf8e30cac85edbb39642c37d248"  # type: ignore[index]
    assert (
        envelope["runtime_identity"]["llama_cpp_commit"]
        == "3173a56471c1753650cd806694145ffd6dcace67"
    )  # type: ignore[index]
    assert envelope["runtime_identity"]["device"] == "none"  # type: ignore[index]
    assert envelope["runtime_identity"]["gpu_layers"] == 0  # type: ignore[index]
    assert envelope["runner_envelope"]["runs_on"] == "ubuntu-24.04"  # type: ignore[index]
    assert envelope["resource_ceiling"]["paid_cost_usd"] == 0.0  # type: ignore[index]
    assert envelope["dispatch_state"] == "BLOCKED_PENDING_CANONICAL_EXECUTOR_TOOLCHAIN_BINDING"
    assert (
        envelope["toolchain_provisioning"]["state"]
        == "BLOCKED_PENDING_SEPARATELY_REVIEWED_EXECUTOR_BINDING"
    )  # type: ignore[index]


def test_t031_scope_does_not_contain_b012_candidate_ids() -> None:
    envelope = _load(ENVELOPE)
    candidate_ids = set(envelope["candidate_ids"])  # type: ignore[arg-type]
    assert "mellum-4b" not in candidate_ids
    assert "qwen3.5-0.8b-control" not in candidate_ids
