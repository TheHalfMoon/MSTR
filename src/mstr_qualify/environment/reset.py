"""A012 clean-checkout environment reset/setup abstraction.

The module executes only repository-local reset operations itself. Arbitrary setup
commands run through an injected executor that must attest the exact effect and
resource envelope it enforces. Environment admission remains A013 authority.
"""

from __future__ import annotations

import json
import subprocess
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from mstr_qualify.errors import QualificationError
from mstr_qualify.schemas import validate_instance


class EnvironmentResetError(QualificationError):
    """Fail-closed A012 error with a stable machine code."""

    default_code = "environment.reset"


@dataclass(frozen=True, slots=True)
class EffectEnvelope:
    network_access: str
    allowed_hosts: tuple[str, ...]
    secret_access: bool
    allowed_secret_ids: tuple[str, ...]
    filesystem_writes: str
    subprocess_execution: bool
    authority_id: str | None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> EffectEnvelope:
        return cls(
            network_access=str(value["network_access"]),
            allowed_hosts=tuple(str(item) for item in value["allowed_hosts"]),
            secret_access=bool(value["secret_access"]),
            allowed_secret_ids=tuple(str(item) for item in value["allowed_secret_ids"]),
            filesystem_writes=str(value["filesystem_writes"]),
            subprocess_execution=bool(value["subprocess_execution"]),
            authority_id=None if value["authority_id"] is None else str(value["authority_id"]),
        )


@dataclass(frozen=True, slots=True)
class ResourceEnvelope:
    wall_clock_seconds: int
    memory_mib: int
    disk_mib: int
    process_count: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ResourceEnvelope:
        return cls(
            wall_clock_seconds=int(value["wall_clock_seconds"]),
            memory_mib=int(value["memory_mib"]),
            disk_mib=int(value["disk_mib"]),
            process_count=int(value["process_count"]),
        )


@dataclass(frozen=True, slots=True)
class ExecutorEnvelope:
    effects: EffectEnvelope
    resources: ResourceEnvelope


@dataclass(frozen=True, slots=True)
class CommandResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


class SetupExecutor(Protocol):
    """Injected setup executor whose enforcement identity is explicit."""

    @property
    def envelope(self) -> ExecutorEnvelope: ...

    def run(self, argv: tuple[str, ...], *, cwd: Path, timeout_seconds: int) -> CommandResult: ...


class FreshCloneDriver(Protocol):
    """Injected fresh-clone mechanism; A012 never opens network implicitly."""

    def materialize(
        self,
        repository_url: str,
        revision_sha: str,
        destination: Path,
        *,
        timeout_seconds: int,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class SetupStepRecord:
    step_id: str
    argv: tuple[str, ...]
    working_directory: str
    timeout_seconds: int
    exit_code: int


@dataclass(frozen=True, slots=True)
class EnvironmentSetupRecord:
    environment_id: str
    repository_url: str
    repository_revision: str
    repository_tree: str
    setup_manifest_id: str
    reset_mode: str
    health_target_ids: tuple[str, ...]
    independent_checker_ids: tuple[str, ...]
    effects: EffectEnvelope
    resources: ResourceEnvelope
    setup_steps: tuple[SetupStepRecord, ...]
    admission_status: str = "NOT_EVALUATED_A013"


def _fail(message: str, code: str, **details: object) -> EnvironmentResetError:
    return EnvironmentResetError(message, code=code, details=details)


def _load_json(path: Path, schema_name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise _fail("unable to read manifest", "environment.manifest_read", path=str(path)) from exc
    except json.JSONDecodeError as exc:
        raise _fail(
            "manifest is not valid JSON",
            "environment.manifest_json",
            path=str(path),
            reason=exc.msg,
        ) from exc
    if not isinstance(value, dict):
        raise _fail("manifest root must be an object", "environment.manifest_root", path=str(path))
    validate_instance(schema_name, value)
    return value


def _git(workspace: Path, *args: str, timeout_seconds: int) -> str:
    try:
        completed = subprocess.run(
            ("git", "-C", str(workspace), *args),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("local git operation failed", "environment.git_execution", args=" ".join(args)) from exc
    if completed.returncode != 0:
        raise _fail(
            "local git operation failed",
            "environment.git_failure",
            args=" ".join(args),
            exit_code=completed.returncode,
            stderr=completed.stderr[-2000:],
        )
    return completed.stdout.strip()


def _normalize_repository_url(value: str) -> str:
    return value[:-4] if value.endswith(".git") else value


def _assert_repository_identity(workspace: Path, repository: Mapping[str, Any], timeout: int) -> None:
    expected_url = _normalize_repository_url(str(repository["repository_url"]))
    observed_url = _normalize_repository_url(_git(workspace, "remote", "get-url", "origin", timeout_seconds=timeout))
    if observed_url != expected_url:
        raise _fail(
            "repository origin does not match manifest",
            "environment.repository_url_mismatch",
            expected=expected_url,
            observed=observed_url,
        )
    expected_revision = str(repository["revision_sha"])
    observed_revision = _git(workspace, "rev-parse", "HEAD", timeout_seconds=timeout)
    if observed_revision != expected_revision:
        raise _fail(
            "repository revision does not match manifest",
            "environment.revision_mismatch",
            expected=expected_revision,
            observed=observed_revision,
        )
    expected_tree = str(repository["tree_sha"])
    observed_tree = _git(workspace, "rev-parse", "HEAD^{tree}", timeout_seconds=timeout)
    if observed_tree != expected_tree:
        raise _fail(
            "repository tree does not match manifest",
            "environment.tree_mismatch",
            expected=expected_tree,
            observed=observed_tree,
        )


def _assert_clean(workspace: Path, timeout: int) -> None:
    dirty = _git(
        workspace,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        timeout_seconds=timeout,
    )
    if dirty:
        raise _fail("workspace is not clean after reset", "environment.reset_not_clean", status=dirty)


def _assert_protected_clean(workspace: Path, protected_paths: Sequence[str], timeout: int) -> None:
    if not protected_paths:
        return
    dirty = _git(
        workspace,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        *protected_paths,
        timeout_seconds=timeout,
    )
    if dirty:
        raise _fail(
            "setup modified a protected path",
            "environment.protected_path_modified",
            status=dirty,
        )


def _contained_directory(workspace: Path, relative: str) -> Path:
    root = workspace.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise _fail(
            "setup working directory escapes workspace",
            "environment.working_directory_escape",
            working_directory=relative,
        ) from exc
    if not candidate.is_dir():
        raise _fail(
            "setup working directory does not exist",
            "environment.working_directory_missing",
            working_directory=relative,
        )
    return candidate


def _cross_bind(environment: Mapping[str, Any], setup: Mapping[str, Any]) -> tuple[EffectEnvelope, ResourceEnvelope]:
    checks = (
        ("environment_id", environment["environment_id"], setup["environment_id"]),
        ("setup_manifest_id", environment["setup_manifest_id"], setup["setup_manifest_id"]),
        ("health_target_ids", environment["health_target_ids"], setup["health_target_ids"]),
        ("effect_policy", environment["effect_policy"], setup["effect_policy"]),
        ("resource_limits", environment["resource_limits"], setup["resource_limits"]),
    )
    for field, left, right in checks:
        if left != right:
            raise _fail(
                "environment/setup manifest binding mismatch",
                "environment.manifest_binding",
                field=field,
            )
    return (
        EffectEnvelope.from_mapping(environment["effect_policy"]),
        ResourceEnvelope.from_mapping(environment["resource_limits"]),
    )


def _assert_authority(effects: EffectEnvelope, authority_ids: frozenset[str]) -> None:
    requires_authority = effects.network_access != "NONE" or effects.secret_access
    if requires_authority:
        if effects.authority_id is None or effects.authority_id not in authority_ids:
            raise _fail(
                "effect envelope requires an exact runtime authority",
                "environment.authority_missing",
                authority_id=effects.authority_id,
            )
    elif effects.authority_id is not None:
        raise _fail(
            "authority_id is not valid for a no-network/no-secret setup",
            "environment.authority_unneeded",
            authority_id=effects.authority_id,
        )


def _reset_workspace(
    workspace: Path,
    environment: Mapping[str, Any],
    *,
    fresh_clone_driver: FreshCloneDriver | None,
) -> None:
    repository = environment["repository_identity"]
    reset = environment["reset_policy"]
    timeout = int(reset["max_reset_seconds"])
    mode = str(reset["mode"])
    if mode == "FRESH_CLONE":
        if fresh_clone_driver is None:
            raise _fail(
                "FRESH_CLONE requires an injected driver; A012 does not open network implicitly",
                "environment.fresh_clone_driver_required",
            )
        fresh_clone_driver.materialize(
            str(repository["repository_url"]),
            str(repository["revision_sha"]),
            workspace,
            timeout_seconds=timeout,
        )
    elif mode == "HARD_RESET_CLEAN":
        if not (workspace / ".git").exists():
            raise _fail("workspace is not a git checkout", "environment.git_checkout_required")
        _git(workspace, "rev-parse", "--verify", f"{repository['revision_sha']}^{{commit}}", timeout_seconds=timeout)
        _git(workspace, "reset", "--hard", str(repository["revision_sha"]), timeout_seconds=timeout)
        _git(workspace, "clean", "-ffdx", timeout_seconds=timeout)
    else:
        raise _fail("unsupported reset mode", "environment.reset_mode", mode=mode)
    _assert_repository_identity(workspace, repository, timeout)
    _assert_clean(workspace, timeout)


def prepare_environment(
    workspace: Path,
    environment_manifest: Path,
    setup_manifest: Path,
    *,
    executor: SetupExecutor,
    authority_ids: frozenset[str] = frozenset(),
    fresh_clone_driver: FreshCloneDriver | None = None,
) -> EnvironmentSetupRecord:
    """Reset one exact checkout and execute its setup recipe without admitting it.

    The returned record is evidence for A013's independent health/admission loop.
    """

    environment = _load_json(environment_manifest, "mstr-environment-manifest-v0")
    setup = _load_json(setup_manifest, "mstr-setup-manifest-v0")
    effects, resources = _cross_bind(environment, setup)
    _assert_authority(effects, authority_ids)
    if not effects.subprocess_execution:
        raise _fail(
            "setup recipe requires subprocess execution but policy forbids it",
            "environment.subprocess_forbidden",
        )
    expected_envelope = ExecutorEnvelope(effects=effects, resources=resources)
    if executor.envelope != expected_envelope:
        raise _fail(
            "setup executor does not enforce the exact manifest envelope",
            "environment.executor_envelope_mismatch",
        )

    workspace = workspace.resolve()
    _reset_workspace(workspace, environment, fresh_clone_driver=fresh_clone_driver)
    protected = tuple(str(item) for item in environment["protected_paths"])
    reset_timeout = int(environment["reset_policy"]["max_reset_seconds"])
    _assert_protected_clean(workspace, protected, reset_timeout)

    started = time.monotonic()
    records: list[SetupStepRecord] = []
    for raw_step in setup["steps"]:
        elapsed = time.monotonic() - started
        remaining = resources.wall_clock_seconds - elapsed
        if remaining <= 0:
            raise _fail("setup exceeded wall-clock resource limit", "environment.wall_clock_exceeded")
        step_timeout = int(raw_step["timeout_seconds"])
        effective_timeout = max(1, min(step_timeout, int(remaining)))
        cwd = _contained_directory(workspace, str(raw_step["working_directory"]))
        argv = tuple(str(item) for item in raw_step["argv"])
        result = executor.run(argv, cwd=cwd, timeout_seconds=effective_timeout)
        if result.timed_out:
            raise _fail(
                "setup step timed out",
                "environment.setup_timeout",
                step_id=str(raw_step["step_id"]),
            )
        if result.exit_code != 0:
            raise _fail(
                "setup step failed",
                "environment.setup_failure",
                step_id=str(raw_step["step_id"]),
                exit_code=result.exit_code,
                stderr=result.stderr[-2000:],
            )
        _assert_protected_clean(workspace, protected, reset_timeout)
        records.append(
            SetupStepRecord(
                step_id=str(raw_step["step_id"]),
                argv=argv,
                working_directory=str(raw_step["working_directory"]),
                timeout_seconds=effective_timeout,
                exit_code=result.exit_code,
            )
        )

    repository = environment["repository_identity"]
    return EnvironmentSetupRecord(
        environment_id=str(environment["environment_id"]),
        repository_url=str(repository["repository_url"]),
        repository_revision=str(repository["revision_sha"]),
        repository_tree=str(repository["tree_sha"]),
        setup_manifest_id=str(setup["setup_manifest_id"]),
        reset_mode=str(environment["reset_policy"]["mode"]),
        health_target_ids=tuple(str(item) for item in environment["health_target_ids"]),
        independent_checker_ids=tuple(str(item) for item in setup["independent_checker_ids"]),
        effects=effects,
        resources=resources,
        setup_steps=tuple(records),
    )
