"""B023 deterministic verifier-health evaluation on controlled evidence.

The evaluator consumes repository-local evidence observations and emits the
already-frozen B022 ``mstr.verifier-health.v0`` record. It does not execute a
verifier, create terminal success, run a model, access model weights, or grant
training authority. A006 remains the protected terminal-success authority and
A018 remains the trajectory-admission authority surface.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from mstr_qualify.errors import QualificationError
from mstr_qualify.schemas import validate_instance

HealthClass = Literal[
    "HEALTHY",
    "PARTIAL",
    "DISAGREEMENT",
    "BROKEN",
    "LEAKED",
    "TAMPERED",
]
CheckStatus = Literal["PASS", "FAIL", "NOT_APPLICABLE"]
ProtectedPathIntegrity = Literal["PASS", "FAIL"]
GeneratedTestIndependence = Literal[
    "INDEPENDENT",
    "PARTIAL",
    "NOT_INDEPENDENT",
    "NOT_APPLICABLE",
    "UNRESOLVED",
]


class VerifierHealthEvaluationError(QualificationError):
    """Fail-closed B023 evaluator error with a stable machine code."""

    default_code = "verifier.health"


@dataclass(frozen=True, slots=True)
class VerifierHealthObservation:
    """Controlled, already-observed evidence used to derive verifier health."""

    verifier_health_id: str
    task_identity: str
    verifier_manifest_id: str
    evaluator_hashes: tuple[Mapping[str, Any], ...]
    protected_paths: tuple[str, ...]
    protected_path_integrity: ProtectedPathIntegrity
    reference_oracle_status: CheckStatus
    noop_fail_status: CheckStatus
    known_bad_fail_status: CheckStatus
    mutation_results: tuple[Mapping[str, Any], ...]
    generated_test_independence: GeneratedTestIndependence
    leakage_checks: tuple[Mapping[str, Any], ...]
    disagreement_signals: tuple[Mapping[str, Any], ...]


def _mutation_mismatch(observation: VerifierHealthObservation) -> bool:
    for result in observation.mutation_results:
        expected = result.get("expected_rejection")
        observed = result.get("observed_rejection")
        if isinstance(expected, bool) and isinstance(observed, bool) and expected != observed:
            return True
    return False


def classify_verifier_health(observation: VerifierHealthObservation) -> HealthClass:
    """Classify one controlled observation with safety-first deterministic precedence."""

    if observation.protected_path_integrity == "FAIL":
        return "TAMPERED"

    if any(check.get("status") == "DETECTED" for check in observation.leakage_checks):
        return "LEAKED"

    if (
        observation.reference_oracle_status == "FAIL"
        or observation.noop_fail_status == "FAIL"
        or observation.known_bad_fail_status == "FAIL"
        or _mutation_mismatch(observation)
    ):
        return "BROKEN"

    if any(signal.get("status") == "DISAGREE" for signal in observation.disagreement_signals):
        return "DISAGREEMENT"

    if (
        observation.generated_test_independence
        in {"PARTIAL", "NOT_INDEPENDENT", "UNRESOLVED"}
        or any(
            signal.get("status") == "INDETERMINATE"
            for signal in observation.disagreement_signals
        )
    ):
        return "PARTIAL"

    return "HEALTHY"


def _stage_eligibility(
    health_class: HealthClass, stage_ids: Sequence[str]
) -> list[dict[str, Any]]:
    if not stage_ids or any(
        not isinstance(stage_id, str) or not stage_id.strip() for stage_id in stage_ids
    ):
        raise VerifierHealthEvaluationError(
            "verifier-health evaluation requires non-empty stage identities",
            code="verifier.health_stage_invalid",
        )
    if len(set(stage_ids)) != len(stage_ids):
        raise VerifierHealthEvaluationError(
            "verifier-health stage identities must be unique",
            code="verifier.health_stage_duplicate",
        )

    if health_class == "HEALTHY":
        admission_class = "CLEAN_POSITIVE_ELIGIBLE"
        reason_codes: list[str] = []
    elif health_class in {"PARTIAL", "DISAGREEMENT"}:
        admission_class = "RESEARCH_DIAGNOSTIC_ONLY"
        reason_codes = [f"VERIFIER_HEALTH_{health_class}"]
    else:
        admission_class = "BLOCKED"
        reason_codes = [f"VERIFIER_HEALTH_{health_class}"]

    return [
        {
            "stage_id": stage_id,
            "admission_class": admission_class,
            "reason_codes": list(reason_codes),
        }
        for stage_id in stage_ids
    ]


def evaluate_verifier_health(
    observation: VerifierHealthObservation,
    *,
    stage_ids: Sequence[str],
) -> dict[str, Any]:
    """Emit one schema-valid B022 health record from controlled B023 evidence."""

    health_class = classify_verifier_health(observation)
    record: dict[str, Any] = {
        "schema_version": "mstr.verifier-health.v0",
        "verifier_health_id": observation.verifier_health_id,
        "task_identity": observation.task_identity,
        "verifier_manifest_id": observation.verifier_manifest_id,
        "evaluator_hashes": [dict(item) for item in observation.evaluator_hashes],
        "protected_paths": list(observation.protected_paths),
        "protected_path_integrity": observation.protected_path_integrity,
        "reference_oracle_status": observation.reference_oracle_status,
        "noop_fail_status": observation.noop_fail_status,
        "known_bad_fail_status": observation.known_bad_fail_status,
        "mutation_results": [dict(item) for item in observation.mutation_results],
        "generated_test_independence": observation.generated_test_independence,
        "leakage_checks": [dict(item) for item in observation.leakage_checks],
        "disagreement_signals": [dict(item) for item in observation.disagreement_signals],
        "health_class": health_class,
        "training_stage_eligibility": _stage_eligibility(health_class, stage_ids),
    }
    validate_instance("mstr-verifier-health-v0", record)
    return record
