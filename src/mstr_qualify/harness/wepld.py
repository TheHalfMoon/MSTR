"""A009: H2 WePLD-native adapter over the canonical MSTR harness spine.

H2 is an integration surface, not a second agent runtime. It maps portable
WePLD goal/spec/task/effect/verifier state into H1/MSTR loop inputs while
preserving MSTR's standalone operation and A006 as the only canonical success
authority. No WePLD package import or network service is required.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mstr_qualify.harness.build_loop import LoopSnapshot
from mstr_qualify.harness.native import NativeHarness, NativeHarnessError
from mstr_qualify.harness.neutral import CommandRunner
from mstr_qualify.state import CompactionPolicy

_PROFILE_ID = "mstr.harness.h2-wepld-native.v0"
_CONTRACT_ID = "mstr.wepld-adapter.v0"


class WePLDAdapterError(NativeHarnessError):
    """Fail-closed H2 adapter error with a stable machine code."""


@dataclass(frozen=True)
class WePLDGoalState:
    goal_id: str
    direction: str
    acceptance_criteria: tuple[str, ...]
    constraints: tuple[str, ...] = ()
    non_goals: tuple[str, ...] = ()


@dataclass(frozen=True)
class WePLDSpecState:
    spec_id: str
    revision: str
    requirements: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class WePLDTaskState:
    task_id: str
    revision: str
    acceptance_criteria: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class WePLDEffectState:
    effect_envelope_id: str
    allowed_effects: tuple[str, ...] = ()
    prohibited_effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class WePLDVerifierState:
    required_verifier_ids: tuple[str, ...]
    policy_id: str


@dataclass(frozen=True)
class WePLDWorkItem:
    goal: WePLDGoalState
    spec: WePLDSpecState
    task: WePLDTaskState
    effects: WePLDEffectState
    verifier: WePLDVerifierState


@dataclass(frozen=True)
class WePLDAdapterBinding:
    profile_id: str
    contract_id: str
    goal_id: str
    spec_identity: str
    task_identity: str
    effect_envelope_id: str
    verifier_policy_id: str
    required_verifier_ids: tuple[str, ...]
    binding_sha256: str
    loop: LoopSnapshot


def _canonical_text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise WePLDAdapterError(
            f"{field} must be a non-empty canonical string",
            code="h2.wepld_state_invalid",
        )
    return value


def _canonical_texts(values: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise WePLDAdapterError(
            f"{field} must be a list of canonical strings",
            code="h2.wepld_state_invalid",
        )
    result = tuple(_canonical_text(value, field=field) for value in values)
    if len(set(result)) != len(result):
        raise WePLDAdapterError(
            f"{field} must not contain duplicates",
            code="h2.wepld_state_invalid",
        )
    return result


def _require_keys(
    value: object,
    *,
    field: str,
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WePLDAdapterError(
            f"{field} must be an object",
            code="h2.wepld_state_invalid",
        )
    if any(not isinstance(key, str) for key in value):
        raise WePLDAdapterError(
            f"{field} field names must be strings",
            code="h2.wepld_state_invalid",
        )
    keys = set(value)
    allowed = required | optional
    missing = sorted(required - keys)
    extra = sorted(keys - allowed)
    if missing or extra:
        detail = []
        if missing:
            detail.append(f"missing={missing}")
        if extra:
            detail.append(f"extra={extra}")
        raise WePLDAdapterError(
            f"{field} has invalid fields ({', '.join(detail)})",
            code="h2.wepld_state_invalid",
        )
    return value


def work_item_from_mapping(payload: Mapping[str, Any]) -> WePLDWorkItem:
    """Parse a portable WePLD state bundle and reject unknown authority fields."""

    root = _require_keys(
        payload,
        field="wepld",
        required=frozenset({"contract_id", "goal", "spec", "task", "effects", "verifier"}),
    )
    if _canonical_text(root["contract_id"], field="contract_id") != _CONTRACT_ID:
        raise WePLDAdapterError(
            "unsupported WePLD adapter contract",
            code="h2.contract_mismatch",
        )

    goal = _require_keys(
        root["goal"],
        field="goal",
        required=frozenset({"goal_id", "direction", "acceptance_criteria"}),
        optional=frozenset({"constraints", "non_goals"}),
    )
    spec = _require_keys(
        root["spec"],
        field="spec",
        required=frozenset({"spec_id", "revision"}),
        optional=frozenset({"requirements", "constraints"}),
    )
    task = _require_keys(
        root["task"],
        field="task",
        required=frozenset({"task_id", "revision"}),
        optional=frozenset({"acceptance_criteria", "constraints"}),
    )
    effects = _require_keys(
        root["effects"],
        field="effects",
        required=frozenset({"effect_envelope_id"}),
        optional=frozenset({"allowed_effects", "prohibited_effects"}),
    )
    verifier = _require_keys(
        root["verifier"],
        field="verifier",
        required=frozenset({"required_verifier_ids", "policy_id"}),
    )

    return WePLDWorkItem(
        goal=WePLDGoalState(
            goal_id=_canonical_text(goal["goal_id"], field="goal.goal_id"),
            direction=_canonical_text(goal["direction"], field="goal.direction"),
            acceptance_criteria=_canonical_texts(
                goal["acceptance_criteria"], field="goal.acceptance_criteria"
            ),
            constraints=_canonical_texts(
                goal.get("constraints", ()), field="goal.constraints"
            ),
            non_goals=_canonical_texts(goal.get("non_goals", ()), field="goal.non_goals"),
        ),
        spec=WePLDSpecState(
            spec_id=_canonical_text(spec["spec_id"], field="spec.spec_id"),
            revision=_canonical_text(spec["revision"], field="spec.revision"),
            requirements=_canonical_texts(
                spec.get("requirements", ()), field="spec.requirements"
            ),
            constraints=_canonical_texts(
                spec.get("constraints", ()), field="spec.constraints"
            ),
        ),
        task=WePLDTaskState(
            task_id=_canonical_text(task["task_id"], field="task.task_id"),
            revision=_canonical_text(task["revision"], field="task.revision"),
            acceptance_criteria=_canonical_texts(
                task.get("acceptance_criteria", ()), field="task.acceptance_criteria"
            ),
            constraints=_canonical_texts(
                task.get("constraints", ()), field="task.constraints"
            ),
        ),
        effects=WePLDEffectState(
            effect_envelope_id=_canonical_text(
                effects["effect_envelope_id"], field="effects.effect_envelope_id"
            ),
            allowed_effects=_canonical_texts(
                effects.get("allowed_effects", ()), field="effects.allowed_effects"
            ),
            prohibited_effects=_canonical_texts(
                effects.get("prohibited_effects", ()), field="effects.prohibited_effects"
            ),
        ),
        verifier=WePLDVerifierState(
            required_verifier_ids=_canonical_texts(
                verifier["required_verifier_ids"],
                field="verifier.required_verifier_ids",
            ),
            policy_id=_canonical_text(verifier["policy_id"], field="verifier.policy_id"),
        ),
    )


def _validate_work_item(work_item: WePLDWorkItem) -> None:
    _canonical_text(work_item.goal.goal_id, field="goal.goal_id")
    _canonical_text(work_item.goal.direction, field="goal.direction")
    _canonical_texts(work_item.goal.acceptance_criteria, field="goal.acceptance_criteria")
    _canonical_texts(work_item.goal.constraints, field="goal.constraints")
    _canonical_texts(work_item.goal.non_goals, field="goal.non_goals")
    _canonical_text(work_item.spec.spec_id, field="spec.spec_id")
    _canonical_text(work_item.spec.revision, field="spec.revision")
    _canonical_texts(work_item.spec.requirements, field="spec.requirements")
    _canonical_texts(work_item.spec.constraints, field="spec.constraints")
    _canonical_text(work_item.task.task_id, field="task.task_id")
    _canonical_text(work_item.task.revision, field="task.revision")
    _canonical_texts(work_item.task.acceptance_criteria, field="task.acceptance_criteria")
    _canonical_texts(work_item.task.constraints, field="task.constraints")
    _canonical_text(
        work_item.effects.effect_envelope_id,
        field="effects.effect_envelope_id",
    )
    _canonical_texts(work_item.effects.allowed_effects, field="effects.allowed_effects")
    _canonical_texts(
        work_item.effects.prohibited_effects,
        field="effects.prohibited_effects",
    )
    _canonical_texts(
        work_item.verifier.required_verifier_ids,
        field="verifier.required_verifier_ids",
    )
    _canonical_text(work_item.verifier.policy_id, field="verifier.policy_id")


def _dedupe(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _binding_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class WePLDNativeHarness(NativeHarness):
    """H2 adapter that narrows portable WePLD state into canonical MSTR inputs."""

    def __init__(
        self,
        workspace: Path,
        contract: Mapping[str, Any],
        *,
        run_id: str,
        required_verifier_ids: Sequence[str],
        command_runner: CommandRunner | None = None,
        max_search_matches: int = 100,
        context_max_files: int = 8,
        context_max_chars: int = 8192,
        compaction_policy: CompactionPolicy | None = None,
    ) -> None:
        effect_envelope_id = contract.get("effect_envelope_id")
        self._h2_effect_envelope_id = _canonical_text(
            effect_envelope_id, field="contract.effect_envelope_id"
        )
        canonical_verifiers = _canonical_texts(
            tuple(required_verifier_ids),
            field="required_verifier_ids",
        )
        self._h2_required_verifier_ids = tuple(sorted(canonical_verifiers))
        super().__init__(
            workspace,
            contract,
            run_id=run_id,
            required_verifier_ids=canonical_verifiers,
            command_runner=command_runner,
            max_search_matches=max_search_matches,
            context_max_files=context_max_files,
            context_max_chars=context_max_chars,
            compaction_policy=compaction_policy,
        )

    def admit_wepld(self, work_item: WePLDWorkItem) -> WePLDAdapterBinding:
        """Admit exact WePLD work state without widening MSTR authority."""

        _validate_work_item(work_item)
        if work_item.effects.effect_envelope_id != self._h2_effect_envelope_id:
            raise WePLDAdapterError(
                "WePLD effect envelope must exactly match the active MSTR loop contract",
                code="h2.effect_envelope_expansion_forbidden",
            )
        overlap = set(work_item.effects.allowed_effects) & set(
            work_item.effects.prohibited_effects
        )
        if overlap:
            raise WePLDAdapterError(
                "WePLD allowed/prohibited effect sets must be disjoint",
                code="h2.effect_policy_conflict",
            )

        observed_verifiers = tuple(sorted(work_item.verifier.required_verifier_ids))
        if observed_verifiers != self._h2_required_verifier_ids:
            raise WePLDAdapterError(
                "WePLD verifier set must exactly match the required MSTR verifier set",
                code="h2.verifier_set_mismatch",
            )

        acceptance_criteria = _dedupe(
            (
                *work_item.goal.acceptance_criteria,
                *work_item.spec.requirements,
                *work_item.task.acceptance_criteria,
            )
        )
        constraints = _dedupe(
            (
                *work_item.goal.constraints,
                *work_item.spec.constraints,
                *work_item.task.constraints,
                f"WePLD spec identity: {work_item.spec.spec_id}@{work_item.spec.revision}",
                f"WePLD task identity: {work_item.task.task_id}@{work_item.task.revision}",
                f"WePLD effect envelope: {work_item.effects.effect_envelope_id}",
                *(
                    f"WePLD allowed effect: {effect}"
                    for effect in work_item.effects.allowed_effects
                ),
                *(
                    f"WePLD prohibited effect: {effect}"
                    for effect in work_item.effects.prohibited_effects
                ),
                f"WePLD verifier policy: {work_item.verifier.policy_id}",
            )
        )

        loop = super().admit_goal(
            work_item.goal.direction,
            acceptance_criteria=acceptance_criteria,
            constraints=constraints,
            non_goals=work_item.goal.non_goals,
        )
        spec_identity = f"{work_item.spec.spec_id}@{work_item.spec.revision}"
        task_identity = f"{work_item.task.task_id}@{work_item.task.revision}"
        binding_payload: dict[str, object] = {
            "profile_id": _PROFILE_ID,
            "contract_id": _CONTRACT_ID,
            "goal_id": work_item.goal.goal_id,
            "spec_identity": spec_identity,
            "task_identity": task_identity,
            "effect_envelope_id": work_item.effects.effect_envelope_id,
            "verifier_policy_id": work_item.verifier.policy_id,
            "required_verifier_ids": list(observed_verifiers),
        }
        digest = _binding_digest(binding_payload)
        self._emit(
            "context.observed",
            {"h2_wepld_binding": {**binding_payload, "binding_sha256": digest}},
            source="harness",
            model_visible=True,
        )
        return WePLDAdapterBinding(
            profile_id=_PROFILE_ID,
            contract_id=_CONTRACT_ID,
            goal_id=work_item.goal.goal_id,
            spec_identity=spec_identity,
            task_identity=task_identity,
            effect_envelope_id=work_item.effects.effect_envelope_id,
            verifier_policy_id=work_item.verifier.policy_id,
            required_verifier_ids=observed_verifiers,
            binding_sha256=digest,
            loop=loop,
        )
