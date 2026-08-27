from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from mstr_qualify.errors import QualificationError
from mstr_qualify.task_drift import detect_canonical_drift

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "task_drift_cases.json"


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _catalog_payload(*, b003_state: str = "PENDING") -> dict[str, object]:
    return {
        "catalog_version": "mstr.task-catalog.v0",
        "workstream_id": "MSTR-000B",
        "tasks_file": "specs/002-code-model-supremacy-foundation/tasks.md",
        "defaults": {
            "outputs": [],
            "evidence_outputs": [],
            "candidate_dependent": False,
            "external_effect_class": "NO_EXTERNAL_EFFECT",
            "parallel_safe": False,
            "supersedes": [],
            "superseded_by": [],
            "closeout_rule": {
                "terminal_states": ["COMPLETE_CANONICAL"],
                "require_all_outputs": False,
                "require_all_evidence_outputs": True,
                "completion_requires_merge": True,
            },
        },
        "tasks": {
            "B001": {
                "canonical_state": "COMPLETE_CANONICAL",
                "prerequisites": [],
                "evidence_outputs": ["evidence/mstr-000b/B001.md"],
            },
            "B002": {
                "canonical_state": "COMPLETE_CANONICAL",
                "prerequisites": ["B001"],
                "evidence_outputs": ["evidence/mstr-000b/B002.md"],
            },
            "B003": {
                "canonical_state": b003_state,
                "prerequisites": ["B002"],
                "evidence_outputs": ["evidence/mstr-000b/B003.md"],
            },
        },
    }


def _write_baseline(root: Path) -> None:
    tasks = root / "specs" / "002-code-model-supremacy-foundation" / "tasks.md"
    tasks.parent.mkdir(parents=True)
    tasks.write_text(
        "- [x] **B001 Root task.**\n"
        "  Outputs: fixture.\n\n"
        "- [x] **B002 Gate task.**\n"
        "  Outputs: fixture.\n\n"
        "- [ ] **B003 Drift task.**\n"
        "  Outputs: fixture.\n",
        encoding="utf-8",
    )
    catalog = root / "configs" / "task-gate" / "mstr-000b.json"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(json.dumps(_catalog_payload(), indent=2) + "\n", encoding="utf-8")
    evidence = root / "evidence" / "mstr-000b"
    evidence.mkdir(parents=True)
    (evidence / "B001.md").write_text("**State:** COMPLETE_CANONICAL\n", encoding="utf-8")
    (evidence / "B002.md").write_text("**State:** COMPLETE_CANONICAL\n", encoding="utf-8")


def _init_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "B003 Test")
    _git(root, "config", "user.email", "b003@example.invalid")
    _write_baseline(root)
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture baseline")
    _git(root, "update-ref", "refs/remotes/origin/main", _git(root, "rev-parse", "HEAD"))
    return root


def _commit_main(root: Path, message: str) -> str:
    _git(root, "add", ".")
    _git(root, "commit", "-m", message)
    sha = _git(root, "rev-parse", "HEAD")
    _git(root, "update-ref", "refs/remotes/origin/main", sha)
    return sha


def _write_b003_evidence(
    root: Path,
    *,
    state: str,
    pr_number: int | None = None,
    final_head: str | None = None,
    merge_sha: str | None = None,
    gate_main: str | None = None,
) -> None:
    lines = [f"**State:** {state}"]
    if pr_number is not None:
        lines.append(f"**Implementation PR:** #{pr_number}")
    if final_head is not None:
        lines.append(f"**Final implementation head:** `{final_head}`")
    if merge_sha is not None:
        lines.append(f"**Canonical implementation merge:** `{merge_sha}`")
    if gate_main is not None:
        lines.extend(
            [
                "",
                "```text",
                "ENTRY_GATE_TASK = B003",
                f"ENTRY_GATE_CANONICAL_MAIN = {gate_main}",
                "ENTRY_GATE_ELIGIBLE = true",
                "```",
            ]
        )
    path = root / "evidence" / "mstr-000b" / "B003.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _merge_b003_implementation(root: Path, *, include_gate: bool) -> tuple[str, str, str]:
    gate_main = _git(root, "rev-parse", "HEAD")
    _git(root, "switch", "-c", "impl-b003")
    source = root / "src" / "fixture.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("VALUE = 3\n", encoding="utf-8")
    _write_b003_evidence(
        root,
        state="IMPLEMENTATION_ACTIVE",
        pr_number=3,
        gate_main=gate_main if include_gate else None,
    )
    _git(root, "add", ".")
    _git(root, "commit", "-m", "implement B003 fixture")
    final_head = _git(root, "rev-parse", "HEAD")
    _git(root, "switch", "main")
    _git(
        root,
        "merge",
        "--no-ff",
        "impl-b003",
        "-m",
        "Merge pull request #3 from fixture/impl-b003",
    )
    merge_sha = _git(root, "rev-parse", "HEAD")
    _git(root, "update-ref", "refs/remotes/origin/main", merge_sha)
    return gate_main, final_head, merge_sha


def _close_b003(
    root: Path,
    *,
    gate_main: str,
    final_head: str,
    merge_sha: str,
) -> None:
    tasks = root / "specs" / "002-code-model-supremacy-foundation" / "tasks.md"
    text = tasks.read_text(encoding="utf-8")
    old_block = "- [ ] **B003 Drift task.**\n  Outputs: fixture.\n"
    new_block = (
        "- [x] **B003 Drift task.**\n"
        "  Outputs: fixture.\n"
        f"  Canonical implementation: PR #3 / final head `{final_head}` / merge `{merge_sha}`.\n"
    )
    assert text.count(old_block) == 1
    text = text.replace(old_block, new_block, 1)
    tasks.write_text(text, encoding="utf-8")
    catalog = root / "configs" / "task-gate" / "mstr-000b.json"
    payload = json.loads(catalog.read_text(encoding="utf-8"))
    payload["tasks"]["B003"]["canonical_state"] = "COMPLETE_CANONICAL"
    catalog.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _write_b003_evidence(
        root,
        state="COMPLETE_CANONICAL",
        pr_number=3,
        final_head=final_head,
        merge_sha=merge_sha,
        gate_main=gate_main,
    )
    _commit_main(root, "canonicalize B003 fixture")


def _codes(report: dict[str, object]) -> set[str]:
    findings = report["findings"]
    assert isinstance(findings, list)
    return {str(item["code"]) for item in findings}


def _run_case(name: str, tmp_path: Path) -> set[str]:
    root = _init_repo(tmp_path)
    if name == "clean_pending_successor":
        pass
    elif name == "checkbox_state_conflict":
        tasks = root / "specs" / "002-code-model-supremacy-foundation" / "tasks.md"
        tasks.write_text(
            tasks.read_text(encoding="utf-8").replace(
                "- [x] **B002 Gate task.**",
                "- [ ] **B002 Gate task.**",
                1,
            ),
            encoding="utf-8",
        )
        _commit_main(root, "introduce checkbox drift")
    elif name == "active_evidence_claims_completion":
        _write_b003_evidence(root, state="COMPLETE_CANONICAL")
        _commit_main(root, "introduce evidence drift")
    elif name == "implementation_merged_while_active":
        _merge_b003_implementation(root, include_gate=True)
    elif name in {"valid_terminal_b003", "entry_gate_after_implementation"}:
        gate_main, final_head, merge_sha = _merge_b003_implementation(root, include_gate=True)
        _close_b003(
            root,
            gate_main=gate_main if name == "valid_terminal_b003" else merge_sha,
            final_head=final_head,
            merge_sha=merge_sha,
        )
    else:
        raise AssertionError(f"unknown fixture case: {name}")

    report = detect_canonical_drift(repository_root=root)
    return _codes(report)


def test_fixture_cases_detect_expected_canonical_drift(tmp_path: Path) -> None:
    fixture = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    cases = fixture["cases"]
    assert isinstance(cases, list)
    for index, case in enumerate(cases):
        assert isinstance(case, dict)
        name = str(case["name"])
        expected = {str(value) for value in case["expected_codes"]}
        case_root = tmp_path / f"case-{index}"
        case_root.mkdir()
        observed = _run_case(name, case_root)
        assert expected <= observed, (name, expected, observed)
        if not expected:
            assert observed == set(), (name, observed)


def test_detector_refuses_feature_checkout(tmp_path: Path) -> None:
    root = _init_repo(tmp_path)
    _git(root, "switch", "-c", "feature")
    (root / "feature-only.txt").write_text("diverged\n", encoding="utf-8")
    _git(root, "add", "feature-only.txt")
    _git(root, "commit", "-m", "feature diverges from canonical main")
    with pytest.raises(QualificationError) as captured:
        detect_canonical_drift(repository_root=root)
    assert getattr(captured.value, "code", None) == "task_drift.not_canonical_main"


def test_detector_refuses_dirty_checkout(tmp_path: Path) -> None:
    root = _init_repo(tmp_path)
    (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(QualificationError) as captured:
        detect_canonical_drift(repository_root=root)
    assert getattr(captured.value, "code", None) == "task_drift.dirty_checkout"
