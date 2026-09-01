"""A018: fail-closed trajectory training-admission decisions.

This module consumes already-recorded verifier-health evidence. It does not
execute verifiers, derive verifier-health classes, run models, or train weights.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, cast

from mstr_qualify.schemas import validate_instance

TerminalClass = Literal[
    "VERIFIED_SUCCESS",
    "RECOVERED_SUCCESS",
    "FAILED_VALID",
    "TIMEOUT_VALID",
    "INVALID_ENVIRONMENT",
    "INVALID_VERIFIER",
    "CONTAMINATED",
    "LEAKAGE_DETECTED",
    "AUTHORITY_VIOLATION",
]
ContaminationStatus = Literal["CLEAR", "SUSPECT", "REJECTED"]
TrainingAdmission = Literal[
    "ADMITTED_SFT",
    "ADMITTED_PREFERENCE",
    "ADMITTED_RL_EVIDENCE",
    "EVAL_ONLY",
    "REJECTED",
]
RequestedLane = Literal["SFT", "PREFERENCE", "RL_EVIDENCE", "EVAL_ONLY"]

_SUCCESS_TERMINALS = frozenset({"VERIFIED_SUCCESS", "RECOVERED_SUCCESS"})
_FAILURE_TERMINALS = frozenset({"FAILED_VALID", "TIMEOUT_VALID"})
_HARD_REJECT_TERMINALS = frozenset(
    {
        "INVALID_ENVIRONMENT",
        "INVALID_VERIFIER",
        "CONTAMINATED",
        "LEAKAGE_DETECTED",
        "AUTHORITY_VIOLATION",
    }
)
_PRIVATE_SOURCES = frozenset({"PRIVATE_USER_REPOSITORY", "PRODUCTION_TRACE"})
_BLOCKED_HEALTH = frozenset({"BROKEN", "LEAKED", "TAMPERED"})


class TrajectoryAdmissionError(ValueError):
    """Fail-closed trajectory-admission error with a stable machine code."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class VerifierHealthBinding:
    schema_version: str
    verifier_health_id: str
    task_identity: str
    verifier_manifest_id: str
    health_class: str
    stage_id: str
    stage_admission_class: str

    def as_mapping(self) -> dict[str, str]:
        return {
            "schema_version": self.schema_version,
            "verifier_health_id": self.verifier_health_id,
            "task_identity": self.task_identity,
            "verifier_manifest_id": self.verifier_manifest_id,
            "health_class": self.health_class,
            "stage_id": self.stage_id,
            "stage_admission_class": self.stage_admission_class,
        }


@dataclass(frozen=True)
class AdmissionDecision:
    training_admission: TrainingAdmission
    training_labels: Mapping[str, str]
    admission_reasons: tuple[str, ...]
    verifier_health_binding: VerifierHealthBinding | None

    @property
    def permits_training_ingestion(self) -> bool:
        return self.training_admission.startswith("ADMITTED_")


def bind_verifier_health(
    record: Mapping[str, Any],
    *,
    task_manifest_id: str,
    verifier_manifest_id: str,
    stage_id: str,
) -> VerifierHealthBinding:
    """Validate and bind one exact stage from a canonical verifier-health record."""

    candidate = dict(record)
    validate_instance("mstr-verifier-health-v0", candidate)

    if candidate.get("task_identity") != task_manifest_id:
        raise TrajectoryAdmissionError(
            "verifier health task identity does not match the trajectory run identity",
            code="trajectory.health_task_mismatch",
        )
    if candidate.get("verifier_manifest_id") != verifier_manifest_id:
        raise TrajectoryAdmissionError(
            "verifier health manifest identity does not match the trajectory run identity",
            code="trajectory.health_verifier_mismatch",
        )

    stages = candidate.get("training_stage_eligibility")
    if not isinstance(stages, list):
        raise TrajectoryAdmissionError(
            "verifier health record has no stage eligibility list",
            code="trajectory.health_stage_missing",
        )
    matches = [
        stage
        for stage in stages
        if isinstance(stage, dict) and stage.get("stage_id") == stage_id
    ]
    if len(matches) != 1:
        raise TrajectoryAdmissionError(
            "verifier health record must contain exactly one requested stage",
            code="trajectory.health_stage_ambiguous",
        )
    stage = matches[0]
    return VerifierHealthBinding(
        schema_version=cast(str, candidate["schema_version"]),
        verifier_health_id=cast(str, candidate["verifier_health_id"]),
        task_identity=cast(str, candidate["task_identity"]),
        verifier_manifest_id=cast(str, candidate["verifier_manifest_id"]),
        health_class=cast(str, candidate["health_class"]),
        stage_id=cast(str, stage["stage_id"]),
        stage_admission_class=cast(str, stage["admission_class"]),
    )


def decide_training_admission(
    *,
    terminal_class: TerminalClass,
    requested_lane: RequestedLane,
    provenance: Mapping[str, Any],
    contamination_status: ContaminationStatus,
    authority_violations: tuple[str, ...],
    verifier_health_binding: VerifierHealthBinding | None,
    verifier_proof_present: bool,
) -> AdmissionDecision:
    """Derive a training-admission label without granting execution authority."""

    source_class = provenance.get("source_class")
    provenance_status = provenance.get("provenance_status")
    rights_status = provenance.get("rights_status")
    secret_scan_status = provenance.get("secret_scan_status")

    hard_reasons: list[str] = []
    if source_class in _PRIVATE_SOURCES:
        hard_reasons.append("PRIVATE_OR_PRODUCTION_TRACE_REJECTED_V0")
    if provenance_status != "COMPLETE":
        hard_reasons.append("PROVENANCE_NOT_COMPLETE")
    if rights_status not in {"COMPATIBLE", "NOT_APPLICABLE"}:
        hard_reasons.append("RIGHTS_NOT_COMPATIBLE")
    if secret_scan_status not in {"CLEAR", "NOT_APPLICABLE"}:
        hard_reasons.append("SECRET_SCAN_NOT_CLEAR")
    if contamination_status != "CLEAR":
        hard_reasons.append("CONTAMINATION_NOT_CLEAR")
    if authority_violations:
        hard_reasons.append("AUTHORITY_VIOLATION_PRESENT")
    if terminal_class in _HARD_REJECT_TERMINALS:
        hard_reasons.append("TERMINAL_CLASS_REJECTED")

    if hard_reasons:
        return AdmissionDecision(
            training_admission="REJECTED",
            training_labels={},
            admission_reasons=tuple(sorted(set(hard_reasons))),
            verifier_health_binding=verifier_health_binding,
        )

    if requested_lane == "EVAL_ONLY":
        return AdmissionDecision(
            training_admission="EVAL_ONLY",
            training_labels={},
            admission_reasons=("CALLER_REQUESTED_EVAL_ONLY",),
            verifier_health_binding=verifier_health_binding,
        )

    if verifier_health_binding is None:
        return AdmissionDecision(
            training_admission="REJECTED",
            training_labels={},
            admission_reasons=("VERIFIER_HEALTH_REQUIRED_FOR_TRAINING",),
            verifier_health_binding=None,
        )
    if verifier_health_binding.health_class in _BLOCKED_HEALTH:
        return AdmissionDecision(
            training_admission="REJECTED",
            training_labels={},
            admission_reasons=("VERIFIER_HEALTH_BLOCKED",),
            verifier_health_binding=verifier_health_binding,
        )
    if verifier_health_binding.stage_admission_class == "BLOCKED":
        return AdmissionDecision(
            training_admission="REJECTED",
            training_labels={},
            admission_reasons=("VERIFIER_STAGE_BLOCKED",),
            verifier_health_binding=verifier_health_binding,
        )

    if requested_lane == "SFT":
        if terminal_class not in _SUCCESS_TERMINALS:
            return AdmissionDecision(
                training_admission="REJECTED",
                training_labels={},
                admission_reasons=("SFT_REQUIRES_VERIFIED_SUCCESS",),
                verifier_health_binding=verifier_health_binding,
            )
        if not verifier_proof_present:
            return AdmissionDecision(
                training_admission="REJECTED",
                training_labels={},
                admission_reasons=("SFT_REQUIRES_VERIFIER_PROOF",),
                verifier_health_binding=verifier_health_binding,
            )
        if (
            verifier_health_binding.health_class != "HEALTHY"
            or verifier_health_binding.stage_admission_class != "CLEAN_POSITIVE_ELIGIBLE"
        ):
            return AdmissionDecision(
                training_admission="REJECTED",
                training_labels={},
                admission_reasons=("SFT_REQUIRES_CLEAN_POSITIVE_VERIFIER_HEALTH",),
                verifier_health_binding=verifier_health_binding,
            )
        return AdmissionDecision(
            training_admission="ADMITTED_SFT",
            training_labels={"label_kind": "CLEAN_POSITIVE"},
            admission_reasons=("VERIFIED_SUCCESS_CLEAN_POSITIVE",),
            verifier_health_binding=verifier_health_binding,
        )

    if terminal_class not in _FAILURE_TERMINALS:
        return AdmissionDecision(
            training_admission="REJECTED",
            training_labels={},
            admission_reasons=("FAILURE_LANE_REQUIRES_VALID_FAILURE_OR_TIMEOUT",),
            verifier_health_binding=verifier_health_binding,
        )
    if verifier_health_binding.stage_admission_class not in {
        "CLEAN_POSITIVE_ELIGIBLE",
        "RESEARCH_DIAGNOSTIC_ONLY",
    }:
        return AdmissionDecision(
            training_admission="REJECTED",
            training_labels={},
            admission_reasons=("FAILURE_LANE_VERIFIER_STAGE_NOT_ELIGIBLE",),
            verifier_health_binding=verifier_health_binding,
        )

    if requested_lane == "PREFERENCE":
        return AdmissionDecision(
            training_admission="ADMITTED_PREFERENCE",
            training_labels={"label_kind": "FAILURE_PREFERENCE_EVIDENCE"},
            admission_reasons=("VALID_FAILURE_EVIDENCE",),
            verifier_health_binding=verifier_health_binding,
        )
    return AdmissionDecision(
        training_admission="ADMITTED_RL_EVIDENCE",
        training_labels={"label_kind": "FAILURE_RL_EVIDENCE"},
        admission_reasons=("VALID_FAILURE_EVIDENCE",),
        verifier_health_binding=verifier_health_binding,
    )
