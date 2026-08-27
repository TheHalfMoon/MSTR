from __future__ import annotations

from pathlib import Path

ROOT = Path(".")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} match count: {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_cli() -> None:
    path = ROOT / "src/mstr_qualify/cli.py"
    replace_once(
        path,
        "mstr-qualify task eligible <TASK_ID> --canonical-main <SHA>\n",
        "mstr-qualify task eligible <TASK_ID>\n"
        "mstr-qualify task drift\n",
        "CLI docstring task commands",
    )
    replace_once(
        path,
        "from .task_gate import evaluate_task_eligibility\n",
        "from .task_drift import detect_canonical_drift\n"
        "from .task_gate import evaluate_task_eligibility\n",
        "CLI drift import",
    )
    replace_once(
        path,
        '''def run_task_eligible(task_id: str) -> tuple[int, dict[str, Any]]:\n    """Evaluate one task against the verified canonical-main checkout."""\n\n    result = evaluate_task_eligibility(task_id)\n    exit_code = _EXIT_OK if result["eligible"] else _EXIT_FAIL_CLOSED\n    return exit_code, result\n\n\n# ---------------------------------------------------------------------------\n# parser and dispatch\n''',
        '''def run_task_eligible(task_id: str) -> tuple[int, dict[str, Any]]:\n    """Evaluate one task against the verified canonical-main checkout."""\n\n    result = evaluate_task_eligibility(task_id)\n    exit_code = _EXIT_OK if result["eligible"] else _EXIT_FAIL_CLOSED\n    return exit_code, result\n\n\ndef run_task_drift() -> tuple[int, dict[str, Any]]:\n    """Scan canonical task/evidence/merge state for fail-closed drift."""\n\n    report = detect_canonical_drift()\n    exit_code = _EXIT_OK if report["status"] == "clean" else _EXIT_FAIL_CLOSED\n    return exit_code, report\n\n\n# ---------------------------------------------------------------------------\n# parser and dispatch\n''',
        "CLI drift runner",
    )
    replace_once(
        path,
        '''    task_eligible_parser.add_argument("task_id")\n\n    manifest_parser = subparsers.add_parser(\n''',
        '''    task_eligible_parser.add_argument("task_id")\n    task_subparsers.add_parser(\n        "drift",\n        help="scan canonical task, evidence, and merge state for drift",\n    )\n\n    manifest_parser = subparsers.add_parser(\n''',
        "CLI drift parser",
    )
    replace_once(
        path,
        '''    if args.command == "task":\n        if args.task_command == "eligible":\n            return run_task_eligible(args.task_id)\n        raise QualificationError(\n''',
        '''    if args.command == "task":\n        if args.task_command == "eligible":\n            return run_task_eligible(args.task_id)\n        if args.task_command == "drift":\n            return run_task_drift()\n        raise QualificationError(\n''',
        "CLI drift dispatch",
    )


def patch_unit_test() -> None:
    path = ROOT / "tests/unit/test_task_drift.py"
    replace_once(
        path,
        "from mstr_qualify.task_drift import detect_canonical_drift\n",
        "from mstr_qualify.errors import QualificationError\n"
        "from mstr_qualify.task_drift import detect_canonical_drift\n",
        "unit QualificationError import",
    )
    replace_once(
        path,
        '_FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "task_drift_cases.json"\n',
        '_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "task_drift_cases.json"\n',
        "unit fixture path",
    )
    replace_once(
        path,
        '''    text = text.replace("- [ ] **B003 Drift task.**", "- [x] **B003 Drift task.**", 1)\n    text = text.replace(\n        "  Outputs: fixture.\\n",\n        "  Outputs: fixture.\\n"\n        f"  Canonical implementation: PR #3 / final head `{final_head}` / merge `{merge_sha}`.\\n",\n        1,\n    )\n''',
        '''    old_block = "- [ ] **B003 Drift task.**\\n  Outputs: fixture.\\n"\n    new_block = (\n        "- [x] **B003 Drift task.**\\n"\n        "  Outputs: fixture.\\n"\n        f"  Canonical implementation: PR #3 / final head `{final_head}` / merge `{merge_sha}`.\\n"\n    )\n    assert text.count(old_block) == 1\n    text = text.replace(old_block, new_block, 1)\n''',
        "unit B003 closeout block",
    )
    replace_once(
        path,
        '''def test_detector_refuses_feature_checkout(tmp_path: Path) -> None:\n    root = _init_repo(tmp_path)\n    _git(root, "switch", "-c", "feature")\n    with pytest.raises(Exception) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        '''def test_detector_refuses_feature_checkout(tmp_path: Path) -> None:\n    root = _init_repo(tmp_path)\n    _git(root, "switch", "-c", "feature")\n    (root / "feature-only.txt").write_text("diverged\\n", encoding="utf-8")\n    _git(root, "add", "feature-only.txt")\n    _git(root, "commit", "-m", "feature diverges from canonical main")\n    with pytest.raises(QualificationError) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        "unit feature non-main commit",
    )
    replace_once(
        path,
        '''def test_detector_refuses_dirty_checkout(tmp_path: Path) -> None:\n    root = _init_repo(tmp_path)\n    (root / "dirty.txt").write_text("dirty\\n", encoding="utf-8")\n    with pytest.raises(Exception) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        '''def test_detector_refuses_dirty_checkout(tmp_path: Path) -> None:\n    root = _init_repo(tmp_path)\n    (root / "dirty.txt").write_text("dirty\\n", encoding="utf-8")\n    with pytest.raises(QualificationError) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        "unit dirty exception type",
    )


def patch_ruff_line_wrapping() -> None:
    source = ROOT / "src/mstr_qualify/task_drift.py"
    replacements = [
        (
            '_EVIDENCE_STATE_RE = re.compile(r"^\\*\\*State:\\*\\*\\s*`?(?P<value>[A-Z][A-Z0-9_]*)`?\\s*$", re.MULTILINE)\n',
            '_EVIDENCE_STATE_RE = re.compile(\n    r"^\\*\\*State:\\*\\*\\s*`?(?P<value>[A-Z][A-Z0-9_]*)`?\\s*$",\n    re.MULTILINE,\n)\n',
            "Ruff evidence state regex",
        ),
        (
            '    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all", code="task_drift.status")\n',
            '    status = _git(\n        root,\n        "status",\n        "--porcelain=v1",\n        "--untracked-files=all",\n        code="task_drift.status",\n    )\n',
            "Ruff git status call",
        ),
        (
            '            details={"ancestor": ancestor, "descendant": descendant, "returncode": completed.returncode},\n',
            '            details={\n                "ancestor": ancestor,\n                "descendant": descendant,\n                "returncode": completed.returncode,\n            },\n',
            "Ruff ancestry details",
        ),
        (
            '                _finding(task_id, "git.pr_merge_ambiguous", pr_number=evidence_pr, merges=list(history_merges))\n',
            '                _finding(\n                    task_id,\n                    "git.pr_merge_ambiguous",\n                    pr_number=evidence_pr,\n                    merges=list(history_merges),\n                )\n',
            "Ruff ambiguous merge finding",
        ),
        (
            '        for label, sha in (("final_head", implementation.final_head), ("merge_sha", implementation.merge_sha)):\n',
            '        implementation_commits = (\n            ("final_head", implementation.final_head),\n            ("merge_sha", implementation.merge_sha),\n        )\n        for label, sha in implementation_commits:\n',
            "Ruff implementation commit loop",
        ),
        (
            '                findings.append(_finding(task_id, "git.implementation_commit_missing", field=label, sha=sha))\n',
            '                findings.append(\n                    _finding(\n                        task_id,\n                        "git.implementation_commit_missing",\n                        field=label,\n                        sha=sha,\n                    )\n                )\n',
            "Ruff missing commit finding",
        ),
        (
            '        if _commit_exists(root, implementation.final_head) and _commit_exists(root, implementation.merge_sha):\n',
            '        final_head_exists = _commit_exists(root, implementation.final_head)\n        merge_sha_exists = _commit_exists(root, implementation.merge_sha)\n        if final_head_exists and merge_sha_exists:\n',
            "Ruff implementation existence condition",
        ),
        (
            '            if not _is_ancestor(root, implementation.merge_sha, _git_identity(root, "HEAD", code="task_drift.head_invalid")):\n',
            '            current_head = _git_identity(root, "HEAD", code="task_drift.head_invalid")\n            if not _is_ancestor(root, implementation.merge_sha, current_head):\n',
            "Ruff merge on main condition",
        ),
        (
            '                    _finding(task_id, "entry_gate.task_mismatch", observed=gate_task, expected=task_id)\n',
            '                    _finding(\n                        task_id,\n                        "entry_gate.task_mismatch",\n                        observed=gate_task,\n                        expected=task_id,\n                    )\n',
            "Ruff entry task mismatch",
        ),
        (
            '                findings.append(_finding(task_id, "entry_gate.not_eligible", observed=gate_eligible))\n',
            '                findings.append(\n                    _finding(task_id, "entry_gate.not_eligible", observed=gate_eligible)\n                )\n',
            "Ruff entry not eligible",
        ),
        (
            '            comparison_head = implementation.final_head if implementation is not None else evidence_head\n',
            '            comparison_head = (\n                implementation.final_head if implementation is not None else evidence_head\n            )\n',
            "Ruff comparison head",
        ),
        (
            '                findings.append(_finding(task_id, "entry_gate.final_head_missing", pr_number=evidence_pr))\n',
            '                findings.append(\n                    _finding(\n                        task_id,\n                        "entry_gate.final_head_missing",\n                        pr_number=evidence_pr,\n                    )\n                )\n',
            "Ruff entry final head missing",
        ),
        (
            '            elif comparison_head is not None and _commit_exists(root, str(gate_main)) and _commit_exists(root, comparison_head):\n',
            '            elif (\n                comparison_head is not None\n                and _commit_exists(root, str(gate_main))\n                and _commit_exists(root, comparison_head)\n            ):\n',
            "Ruff entry ancestry condition",
        ),
    ]
    for old, new, label in replacements:
        replace_once(source, old, new, label)

    unit = ROOT / "tests/unit/test_task_drift.py"
    replace_once(
        unit,
        '    _git(root, "merge", "--no-ff", "impl-b003", "-m", "Merge pull request #3 from fixture/impl-b003")\n',
        '    _git(\n        root,\n        "merge",\n        "--no-ff",\n        "impl-b003",\n        "-m",\n        "Merge pull request #3 from fixture/impl-b003",\n    )\n',
        "Ruff unit merge command",
    )


def patch_mypy_iterator_type() -> None:
    source = ROOT / "src/mstr_qualify/task_drift.py"
    replace_once(
        source,
        "from dataclasses import dataclass\n",
        "from collections.abc import Iterator\nfrom dataclasses import dataclass\n",
        "mypy Iterator import",
    )
    replace_once(
        source,
        '        if any(marker in raw for marker in ("*", "?", "[")):\n',
        '        raw_matches: Iterator[Path]\n        if any(marker in raw for marker in ("*", "?", "[")):\n',
        "mypy raw_matches annotation",
    )


def main() -> None:
    patch_cli()
    patch_unit_test()
    patch_ruff_line_wrapping()
    patch_mypy_iterator_type()


if __name__ == "__main__":
    main()
