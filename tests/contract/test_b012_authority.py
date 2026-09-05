from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mstr_qualify.task_gate import evaluate_task_snapshot

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "artifacts/authorities/B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION.json"
ENVELOPE = ROOT / "artifacts/manifests/B012-equivalent-qualification-execution-envelope.json"
B010 = ROOT / "artifacts/manifests/B010-new-candidate-weight-access.json"
_CANONICAL_MAIN = "a" * 40


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_b012_authority_binds_exact_founder_decision_and_b010_candidates() -> None:
    authority = _load(AUTHORITY)
    b010 = _load(B010)
    scope = authority["scope"]
    assert isinstance(scope, dict)
    assert authority["authority_id"] == "B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION"
    assert authority["task_id"] == "B012"
    assert authority["external_effect_class"] == "MODEL_WEIGHT_ACCESS"
    assert authority["status"] == "AUTHORIZED_CANONICAL"
    assert (
        scope["decision"]
        == "FOUNDER_B012_EQUIVALENT_QUALIFICATION_DECISION=AUTHORIZE_EXACT_B010_CANDIDATES"
    )
    assert scope["decision_surface"] == {"issue": 162, "comment_id": 5553875175}
    assert scope["candidate_ids"] == ["mellum-4b", "qwen3.5-0.8b-control"]
    assert scope["candidate_ids"] == b010["decision"]["qualification_candidates"]  # type: ignore[index]
    assert scope["b010_manifest"]["sha256"] == _sha(B010)  # type: ignore[index]
    assert scope["training"] is False
    assert scope["weight_changing_training"] is False
    assert scope["new_candidate_access"] is False


def test_b012_envelope_is_exact_but_dispatch_remains_fail_closed_pending_executor_binding() -> None:
    authority = _load(AUTHORITY)
    envelope = _load(ENVELOPE)
    scope = authority["scope"]
    assert isinstance(scope, dict)
    binding = scope["bounded_execution_envelope"]
    assert isinstance(binding, dict)
    assert (
        binding["path"]
        == "artifacts/manifests/B012-equivalent-qualification-execution-envelope.json"
    )
    assert binding["sha256"] == _sha(ENVELOPE)
    assert envelope["candidate_ids"] == ["mellum-4b", "qwen3.5-0.8b-control"]
    assert envelope["runner_envelope"]["runs_on"] == "ubuntu-24.04"  # type: ignore[index]
    assert (
        envelope["quantization_identity"]["llama_cpp_commit"]
        == "fc35562ba46fbbf8e30cac85edbb39642c37d248"
    )  # type: ignore[index]
    assert (
        envelope["runtime_identity"]["llama_cpp_commit"]
        == "3173a56471c1753650cd806694145ffd6dcace67"
    )  # type: ignore[index]
    assert envelope["resource_ceiling"]["paid_cost_usd"] == 0.0  # type: ignore[index]
    assert envelope["dispatch_state"] == "BLOCKED_PENDING_CANONICAL_EXECUTOR_TOOLCHAIN_BINDING"
    assert (
        envelope["toolchain_provisioning"]["state"]
        == "BLOCKED_PENDING_SEPARATELY_REVIEWED_EXECUTOR_BINDING"
    )  # type: ignore[index]


def test_b012_machine_gate_accepts_canonical_authority_without_broadening_successors() -> None:
    result = evaluate_task_snapshot("B012", canonical_main=_CANONICAL_MAIN)
    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["authority_result"]["satisfied"] is True
    b013 = evaluate_task_snapshot("B013", canonical_main=_CANONICAL_MAIN)
    assert b013["eligible"] is False
    assert "prerequisite.unsatisfied:B012" in b013["reasons"]
