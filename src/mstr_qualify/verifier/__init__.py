"""Protected verifier/finalizer boundary for MSTR-000A."""

from .finalizer import FinalizationDecision, FinalizerError, finalize_run
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
    "REQUIRED_SHORTCUT_CLASSES",
    "RewardShortcutBatteryRecord",
    "ShortcutClass",
    "VerifierFixtureCase",
    "VerifierResult",
    "VerifierRunRecord",
    "VerifierRunnerError",
    "finalize_run",
    "hash_path",
    "run_reward_shortcut_battery",
    "run_verifier_manifest",
]
