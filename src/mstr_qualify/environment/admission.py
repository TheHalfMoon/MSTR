"""A013 bounded environment bootstrap/admission loop.

A013 consumes the A011/A012 environment and setup contracts and adds bounded,
independent health-target admission for repository-controlled local fixtures.
It does not implement the A014 verifier runner or reward-shortcut battery and
must not be used as authority to admit real training/research environments.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from mstr_qualify.errors import QualificationError
from mstr_qualify.schemas import validate_instance

from .reset import (
    EffectEnvelope,
    EnvironmentResetError,
    EnvironmentSetupRecord,
    FreshCloneDriver,
    ResourceEnvelope,
    SetupExecutor,
    prepare_environment,
)


class EnvironmentAdmissionError(QualificationError):
    """Fail-closed A013 admission-contract error with a stable machine code."""

    default_code = "environment.admission"


class EnvironmentHealthCheckError(QualificationError):
    """Typed failure from an injected independent health checker."""

    default_code = "environment.health_check"


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    checker_id: str
    target_id: str
    passed: bool
    detail: str = ""
    error_code: str | None = None


class IndependentHealthChecker(Protocol):
    """Injected checker with explicit identity and local read-only effects."""

    @property
    def checker_id(self) -> str: ...

    @property
    def target_id(self) -> str: ...

    @property
    def effects(self) -> EffectEnvelope: ...

    def check(
        self,
        *,
        workspace: Path,
        setup_record: EnvironmentSetupRecord,
    ) -> HealthCheckResult: ...


@dataclass(frozen=True, slots=True)
class AdmissionAttemptRecord:
    attempt_number: int
    setup_record: EnvironmentSetupRecord | None
    checks: tuple[HealthCheckResult, ...]
    passed: bool
    failure_code: str | None = None
    failure_detail: str = ""


@dataclass(frozen=True, slots=True)
class EnvironmentAdmissionRecord:
    environment_id: str
    setup_manifest_id: str
    verifier_manifest_id: str
    repository_revision: str
    repository_tree: str
    health_target_ids: tuple[str, ...]
    independent_checker_ids: tuple[str, ...]
    max_attempts: int
    attempts: tuple[AdmissionAttemptRecord, ...]
    status: str
    admitted_attempt: int | None


@dataclass(frozen=True, slots=True)
class _AdmissionPlan:
    environment_id: str
    setup_manifest_id: str
    verifier_manifest_id: str
    repository_revision: str
    repository_tree: str
    health_target_ids: tuple[str, ...]
    independent_checker_ids: tuple[str, ...]
    max_attempts: int
    effects: EffectEnvelope
    resources: ResourceEnvelope


def _fail(message: str, code: str, **details: object) -> EnvironmentAdmissionError:
    return EnvironmentAdmissionError(message, code=code, details=details)


def _load_json(path: Path, schema_name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise _fail(
            "unable to read admission manifest",
            "environment.admission_manifest_read",
            path=str(path),
        ) from exc
    except json.JSONDecodeError as exc:
        raise _fail(
            "admission manifest is not valid JSON",
            "environment.admission_manifest_json",
            path=str(path),
            reason=exc.msg,
        ) from exc
    if not isinstance(value, dict):
        raise _fail(
            "admission manifest root must be an object",
            "environment.admission_manifest_root",
            path=str(path),
        )
    validate_instance(schema_name, value)
    return value


def _assert_equal_binding(
    field: str,
    environment: Mapping[str, Any],
    setup: Mapping[str, Any],
) -> None:
    if environment[field] != setup[field]:
        raise _fail(
            "environment/setup admission binding mismatch",
            "environment.admission_manifest_binding",
            field=field,
        )


def _build_plan(
    environment_manifest: Path,
    setup_manifest: Path,
) -> _AdmissionPlan:
    environment = _load_json(environment_manifest, "mstr-environment-manifest-v0")
    setup = _load_json(setup_manifest, "mstr-setup-manifest-v0")

    for field in (
        "environment_id",
        "setup_manifest_id",
        "health_target_ids",
        "effect_policy",
        "resource_limits",
    ):
        _assert_equal_binding(field, environment, setup)

    effects = EffectEnvelope.from_mapping(environment["effect_policy"])
    resources = ResourceEnvelope.from_mapping(environment["resource_limits"])
    if effects.network_access != "NONE" or effects.allowed_hosts:
        raise _fail(
            "A013 fixture admission does not authorize network access",
            "environment.admission_network_not_authorized",
        )
    if effects.secret_access or effects.allowed_secret_ids:
        raise _fail(
            "A013 fixture admission does not authorize secret access",
            "environment.admission_secret_not_authorized",
        )
    if effects.authority_id is not None:
        raise _fail(
            "A013 fixture admission does not consume external-effect authority ids",
            "environment.admission_authority_not_allowed",
            authority_id=effects.authority_id,
        )

    repository = environment["repository_identity"]
    return _AdmissionPlan(
        environment_id=str(environment["environment_id"]),
        setup_manifest_id=str(environment["setup_manifest_id"]),
        verifier_manifest_id=str(environment["verifier_manifest_id"]),
        repository_revision=str(repository["revision_sha"]),
        repository_tree=str(repository["tree_sha"]),
        health_target_ids=tuple(str(item) for item in setup["health_target_ids"]),
        independent_checker_ids=tuple(
            str(item) for item in setup["independent_checker_ids"]
        ),
        max_attempts=int(setup["max_attempts"]),
        effects=effects,
        resources=resources,
    )


def _assert_checker_effects(checker: IndependentHealthChecker) -> None:
    effects = checker.effects
    if effects.network_access != "NONE" or effects.allowed_hosts:
        raise _fail(
            "A013 independent checker must be network-isolated",
            "environment.checker_network_not_allowed",
            checker_id=checker.checker_id,
        )
    if effects.secret_access or effects.allowed_secret_ids:
        raise _fail(
            "A013 independent checker must not access secrets",
            "environment.checker_secret_not_allowed",
            checker_id=checker.checker_id,
        )
    if effects.filesystem_writes != "NONE":
        raise _fail(
            "A013 independent checker must be worktree read-only",
            "environment.checker_write_not_allowed",
            checker_id=checker.checker_id,
            filesystem_writes=effects.filesystem_writes,
        )
    if effects.authority_id is not None:
        raise _fail(
            "A013 independent checker must not consume an external authority id",
            "environment.checker_authority_not_allowed",
            checker_id=checker.checker_id,
            authority_id=effects.authority_id,
        )


def _ordered_checkers(
    plan: _AdmissionPlan,
    checkers: Sequence[IndependentHealthChecker],
) -> tuple[IndependentHealthChecker, ...]:
    by_id: dict[str, IndependentHealthChecker] = {}
    for checker in checkers:
        if not checker.checker_id:
            raise _fail(
                "independent checker id must not be empty",
                "environment.checker_id_empty",
            )
        if checker.checker_id in by_id:
            raise _fail(
                "independent checker ids must be unique",
                "environment.checker_id_duplicate",
                checker_id=checker.checker_id,
            )
        _assert_checker_effects(checker)
        by_id[checker.checker_id] = checker

    expected_ids = set(plan.independent_checker_ids)
    observed_ids = set(by_id)
    if expected_ids != observed_ids:
        raise _fail(
            "injected independent checker ids do not match setup manifest",
            "environment.checker_id_mismatch",
            missing=tuple(sorted(expected_ids - observed_ids)),
            unexpected=tuple(sorted(observed_ids - expected_ids)),
        )

    expected_targets = set(plan.health_target_ids)
    observed_targets = {checker.target_id for checker in checkers}
    if not observed_targets.issubset(expected_targets):
        raise _fail(
            "independent checker targets include undeclared health targets",
            "environment.checker_target_unexpected",
            unexpected=tuple(sorted(observed_targets - expected_targets)),
        )
    if observed_targets != expected_targets:
        raise _fail(
            "every declared health target requires an independent checker",
            "environment.checker_target_missing",
            missing=tuple(sorted(expected_targets - observed_targets)),
        )

    return tuple(by_id[checker_id] for checker_id in plan.independent_checker_ids)


def _validate_result(
    checker: IndependentHealthChecker,
    result: HealthCheckResult,
) -> None:
    if result.checker_id != checker.checker_id or result.target_id != checker.target_id:
        raise _fail(
            "independent checker returned mismatched identity",
            "environment.checker_result_identity",
            expected_checker_id=checker.checker_id,
            observed_checker_id=result.checker_id,
            expected_target_id=checker.target_id,
            observed_target_id=result.target_id,
        )
    if result.passed and result.error_code is not None:
        raise _fail(
            "passing health result must not carry an error code",
            "environment.checker_result_error_code",
            checker_id=checker.checker_id,
            error_code=result.error_code,
        )


def _record(
    plan: _AdmissionPlan,
    attempts: list[AdmissionAttemptRecord],
    *,
    status: str,
    admitted_attempt: int | None,
) -> EnvironmentAdmissionRecord:
    return EnvironmentAdmissionRecord(
        environment_id=plan.environment_id,
        setup_manifest_id=plan.setup_manifest_id,
        verifier_manifest_id=plan.verifier_manifest_id,
        repository_revision=plan.repository_revision,
        repository_tree=plan.repository_tree,
        health_target_ids=plan.health_target_ids,
        independent_checker_ids=plan.independent_checker_ids,
        max_attempts=plan.max_attempts,
        attempts=tuple(attempts),
        status=status,
        admitted_attempt=admitted_attempt,
    )


def admit_environment(
    workspace: Path,
    environment_manifest: Path,
    setup_manifest: Path,
    *,
    executor: SetupExecutor,
    checkers: Sequence[IndependentHealthChecker],
    fresh_clone_driver: FreshCloneDriver | None = None,
) -> EnvironmentAdmissionRecord:
    """Run bounded local setup/check attempts and derive fixture admission.

    Each attempt delegates reset/setup to A012, so retries begin from the exact
    clean-checkout contract. A013 then runs every declared independent checker.
    Admission is derived only when all declared health targets pass within the
    same attempt. Exhaustion returns ``REJECTED`` rather than self-declared
    readiness. This function is restricted to the local controlled-fixture
    boundary until A014 and the remaining environment-execution gates exist.
    """

    plan = _build_plan(environment_manifest, setup_manifest)
    ordered_checkers = _ordered_checkers(plan, checkers)
    attempts: list[AdmissionAttemptRecord] = []
    workspace = workspace.resolve()

    for attempt_number in range(1, plan.max_attempts + 1):
        try:
            setup_record = prepare_environment(
                workspace,
                environment_manifest,
                setup_manifest,
                executor=executor,
                fresh_clone_driver=fresh_clone_driver,
            )
        except EnvironmentResetError as exc:
            attempts.append(
                AdmissionAttemptRecord(
                    attempt_number=attempt_number,
                    setup_record=None,
                    checks=(),
                    passed=False,
                    failure_code=exc.code,
                    failure_detail=str(exc),
                )
            )
            continue

        if setup_record.admission_status != "NOT_EVALUATED_A013":
            raise _fail(
                "A012 setup record carried unexpected admission authority",
                "environment.setup_admission_spoof",
                observed=setup_record.admission_status,
            )
        if setup_record.health_target_ids != plan.health_target_ids:
            raise _fail(
                "A012 setup record health targets do not match A013 plan",
                "environment.setup_health_target_mismatch",
            )
        if setup_record.independent_checker_ids != plan.independent_checker_ids:
            raise _fail(
                "A012 setup record checker ids do not match A013 plan",
                "environment.setup_checker_mismatch",
            )

        check_results: list[HealthCheckResult] = []
        for checker in ordered_checkers:
            try:
                result = checker.check(
                    workspace=workspace,
                    setup_record=setup_record,
                )
            except EnvironmentHealthCheckError as exc:
                result = HealthCheckResult(
                    checker_id=checker.checker_id,
                    target_id=checker.target_id,
                    passed=False,
                    detail=str(exc),
                    error_code=exc.code,
                )
            _validate_result(checker, result)
            check_results.append(result)

        passed = all(result.passed for result in check_results)
        attempts.append(
            AdmissionAttemptRecord(
                attempt_number=attempt_number,
                setup_record=setup_record,
                checks=tuple(check_results),
                passed=passed,
                failure_code=None if passed else "environment.health_target_failed",
                failure_detail="" if passed else "one or more health targets failed",
            )
        )
        if passed:
            return _record(
                plan,
                attempts,
                status="ADMITTED",
                admitted_attempt=attempt_number,
            )

    return _record(
        plan,
        attempts,
        status="REJECTED",
        admitted_attempt=None,
    )
