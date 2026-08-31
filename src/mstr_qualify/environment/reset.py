"""A012 clean-checkout environment reset/setup abstraction.

The module executes only repository-local reset operations itself. Arbitrary setup
commands run through an injected executor that must attest the exact effect and
resource envelope it enforces. Environment admission remains A013 authority.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from collections.abc import Mapping
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

    @property
    def envelope(self) -> ExecutorEnvelope: ...

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


ProtectedSnapshot = tuple[tuple[str, str], ...]


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
        raise _fail(
            "local git operation failed",
            "environment.git_execution",
            args=" ".join(args),
        ) from exc
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


def _assert_repository_origin(
    workspace: Path, repository: Mapping[str, Any], timeout: int
) -> None:
    expected_url = _normalize_repository_url(str(repository["repository_url"]))
    observed_url = _normalize_repository_url(
        _git(workspace, "remote", "get-url", "origin", timeout_seconds=timeout)
    )
    if observed_url != expected_url:
        raise _fail(
            "repository origin does not match manifest",
            "environment.repository_url_mismatch",
            expected=expected_url,
            observed=observed_url,
        )


def _assert_repository_identity(
    workspace: Path, repository: Mapping[str, Any], timeout: int
) -> None:
    _assert_repository_origin(workspace, repository, timeout)
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
        raise _fail(
            "workspace is not clean after reset",
            "environment.reset_not_clean",
            status=dirty,
        )


def _hash_file_into(digest: Any, path: Path) -> None:
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)


def _fingerprint_path(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists() and not path.is_symlink():
        digest.update(b"MISSING")
        return digest.hexdigest()

    def add_node(node: Path, relative_name: str) -> None:
        stat_result = node.lstat()
        digest.update(relative_name.encode("utf-8", errors="surrogateescape"))
        digest.update(str(stat_result.st_mode & 0o7777).encode("ascii"))
        if node.is_symlink():
            digest.update(b"SYMLINK")
            digest.update(str(node.readlink()).encode("utf-8", errors="surrogateescape"))
        elif node.is_dir():
            digest.update(b"DIR")
        elif node.is_file():
            digest.update(b"FILE")
            _hash_file_into(digest, node)
        else:
            digest.update(b"OTHER")

    try:
        add_node(path, ".")
        if path.is_dir() and not path.is_symlink():
            children = sorted(
                path.rglob("*"),
                key=lambda child: child.relative_to(path).as_posix(),
            )
            for child in children:
                add_node(child, child.relative_to(path).as_posix())
    except OSError as exc:
        raise _fail(
            "unable to snapshot protected path",
            "environment.protected_snapshot",
            path=str(path),
        ) from exc
    return digest.hexdigest()


def _snapshot_protected(workspace: Path, protected_paths: tuple[str, ...]) -> ProtectedSnapshot:
    return tuple(
        (relative, _fingerprint_path(workspace / relative))
        for relative in protected_paths
    )


def _assert_protected_unchanged(
    workspace: Path,
    protected_paths: tuple[str, ...],
    expected: ProtectedSnapshot,
) -> None:
    observed = _snapshot_protected(workspace, protected_paths)
    if observed == expected:
        return
    expected_map = dict(expected)
    observed_map = dict(observed)
    changed = tuple(
        relative
        for relative in protected_paths
        if expected_map.get(relative) != observed_map.get(relative)
    )
    raise _fail(
        "setup modified a protected path",
        "environment.protected_path_modified",
        changed_paths=changed,
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


def _cross_bind(
    environment: Mapping[str, Any], setup: Mapping[str, Any]
) -> tuple[EffectEnvelope, ResourceEnvelope]:
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


def _assert_local_effect_boundary(effects: EffectEnvelope) -> None:
    if effects.network_access != "NONE" or effects.secret_access:
        raise _fail(
            "A012 does not authorize network or secret effects",
            "environment.external_effect_not_authorized",
            network_access=effects.network_access,
            secret_access=effects.secret_access,
            authority_id=effects.authority_id,
        )
    if effects.authority_id is not None:
        raise _fail(
            "authority_id is not valid for the A012 local-only execution boundary",
            "environment.authority_unneeded",
            authority_id=effects.authority_id,
        )


def _assert_reset_write_policy(effects: EffectEnvelope) -> None:
    if effects.filesystem_writes != "WORKTREE_AND_TEMP":
        raise _fail(
            "clean-checkout reset requires worktree write authority",
            "environment.reset_write_policy",
            filesystem_writes=effects.filesystem_writes,
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
        _assert_repository_origin(workspace, repository, timeout)
        _git(
            workspace,
            "rev-parse",
            "--verify",
            f"{repository['revision_sha']}^{{commit}}",
            timeout_seconds=timeout,
        )
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
    fresh_clone_driver: FreshCloneDriver | None = None,
) -> EnvironmentSetupRecord:
    """Reset one exact checkout and execute its setup recipe without admitting it.

    A012 is deliberately local-only. Network/secret-bearing manifests fail closed;
    a later canonical task must introduce any externally authorized execution path.
    The returned record is evidence for A013's independent health/admission loop.
    """

    environment = _load_json(environment_manifest, "mstr-environment-manifest-v0")
    setup = _load_json(setup_manifest, "mstr-setup-manifest-v0")
    effects, resources = _cross_bind(environment, setup)
    _assert_local_effect_boundary(effects)
    _assert_reset_write_policy(effects)
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
    if (
        str(environment["reset_policy"]["mode"]) == "FRESH_CLONE"
        and fresh_clone_driver is not None
        and fresh_clone_driver.envelope != expected_envelope
    ):
        raise _fail(
            "fresh-clone driver does not enforce the exact manifest envelope",
            "environment.clone_envelope_mismatch",
        )

    workspace = workspace.resolve()
    _reset_workspace(workspace, environment, fresh_clone_driver=fresh_clone_driver)
    protected = tuple(str(item) for item in environment["protected_paths"])
    protected_snapshot = _snapshot_protected(workspace, protected)

    started = time.monotonic()
    records: list[SetupStepRecord] = []
    for raw_step in setup["steps"]:
        elapsed = time.monotonic() - started
        remaining = resources.wall_clock_seconds - elapsed
        if remaining <= 0:
            raise _fail(
                "setup exceeded wall-clock resource limit",
                "environment.wall_clock_exceeded",
            )
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
        _assert_protected_unchanged(workspace, protected, protected_snapshot)
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