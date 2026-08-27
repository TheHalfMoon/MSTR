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
        '''    with pytest.raises(Exception) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        '''    with pytest.raises(QualificationError) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        "unit feature exception type",
    )
    replace_once(
        path,
        '''    with pytest.raises(Exception) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        '''    with pytest.raises(QualificationError) as captured:\n        detect_canonical_drift(repository_root=root)\n''',
        "unit dirty exception type",
    )


def main() -> None:
    patch_cli()
    patch_unit_test()


if __name__ == "__main__":
    main()
