"""Protected verifier/finalizer boundary for MSTR-000A and B023 health evaluation."""

from .finalizer import FinalizationDecision, FinalizerError, finalize_run
from .health import (
    HealthClass,
    VerifierHealthEvaluationError,
    VerifierHealthObservation,
    classify_verifier_health,
    evaluate_verifier_health,
)
from .runner import (
    REQUIRED_SHORTCUT_CLASSES,
    BatteryCaseResult,
    CommandObservation,
    ControlledVerifierExecutor,
    RewardShortcutBatteryRecord,
    ShortcutClass,
    VerifierFixtureCase,
    VerifierResult,
    VerifierRunnerError,
    VerifierRunRecord,
    hash_path,
    run_reward_shortcut_battery,
    run_verifier_manifest,
)

__all__ = [
    "BatteryCaseResult",
    "CommandObservation",
    "ControlledVerifierExecutor",
    "FinalizationDecision",
    "FinalizerError",
    "HealthClass",
    "REQUIRED_SHORTCUT_CLASSES",
    "RewardShortcutBatteryRecord",
    "ShortcutClass",
    "VerifierFixtureCase",
    "VerifierHealthEvaluationError",
    "VerifierHealthObservation",
    "VerifierResult",
    "VerifierRunRecord",
    "VerifierRunnerError",
    "classify_verifier_health",
    "evaluate_verifier_health",
    "finalize_run",
    "hash_path",
    "run_reward_shortcut_battery",
    "run_verifier_manifest",
]
