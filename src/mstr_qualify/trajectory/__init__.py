"""A018 trajectory recording, replay, and training-admission boundary."""

from .admission import (
    AdmissionDecision,
    TrajectoryAdmissionError,
    VerifierHealthBinding,
    bind_verifier_health,
    decide_training_admission,
)
from .recorder import (
    TrajectoryReplayError,
    build_trajectory_manifest,
    event_log_sha256,
    load_trajectory_bundle,
    record_trajectory_bundle,
    replay_trajectory,
)

__all__ = [
    "AdmissionDecision",
    "TrajectoryAdmissionError",
    "TrajectoryReplayError",
    "VerifierHealthBinding",
    "bind_verifier_health",
    "build_trajectory_manifest",
    "decide_training_admission",
    "event_log_sha256",
    "load_trajectory_bundle",
    "record_trajectory_bundle",
    "replay_trajectory",
]
