from __future__ import annotations

from pathlib import Path
from textwrap import dedent


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} anchor mismatch: {count}")
    return text.replace(old, new, 1)


gate = Path("src/mstr_qualify/task_gate.py")
text = gate.read_text(encoding="utf-8")

start = text.index("def _require_expected_canonical_checkout(\n")
end = text.index("\ndef _node_sha256", start)
replacement = dedent(
    '''\
    def _git_ref(root: Path, ref: str, *, code: str) -> str:
        completed = _run_git(root, "rev-parse", "--verify", ref)
        value = completed.stdout.strip().lower()
        if completed.returncode != 0 or not _HEX40_RE.fullmatch(value):
            raise QualificationError(
                "required canonical Git ref is unavailable or invalid",
                code=code,
                details={"ref": ref, "returncode": completed.returncode, "value": value},
            )
        return value


    def _trusted_canonical_main(root: Path) -> str:
        """Bind eligibility to canonical main refs without performing network I/O.

        Execution governance must refresh and verify ``origin/main`` against live repository
        truth immediately before invoking this offline gate. The gate then refuses any
        checkout where local ``main``, cached ``origin/main``, and ``HEAD`` do not agree.
        """
        head = _git_head(root)
        local_main = _git_ref(root, "refs/heads/main", code="task_gate.main_ref_invalid")
        origin_main = _git_ref(
            root,
            "refs/remotes/origin/main",
            code="task_gate.origin_main_ref_invalid",
        )
        if local_main != origin_main:
            raise QualificationError(
                "local main does not match the refreshed origin/main identity",
                code="task_gate.main_ref_mismatch",
                details={"main": local_main, "origin_main": origin_main},
            )
        if head != local_main:
            raise QualificationError(
                "task eligibility must execute at the canonical main commit",
                code="task_gate.not_canonical_main",
                details={"head": head, "canonical_main": local_main},
            )
        status = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
        if status.returncode != 0:
            raise QualificationError(
                "unable to verify clean canonical checkout",
                code="task_gate.git_status",
                details={"returncode": status.returncode},
            )
        if status.stdout.strip():
            raise QualificationError(
                "task eligibility refuses a dirty canonical checkout",
                code="task_gate.dirty_checkout",
                details={"entries": status.stdout.splitlines()},
            )
        return head
    '''
)
text = text[:start] + replacement + text[end + 1 :]

eval_start = text.index("def evaluate_task_eligibility(\n")
eval_replacement = dedent(
    '''\
    def evaluate_task_eligibility(
        task_id: str,
        *,
        repository_root: Path | None = None,
        catalog_path: Path | None = None,
    ) -> dict[str, Any]:
        """Evaluate one task against the verified canonical-main checkout."""
        root = (repository_root or _REPOSITORY_ROOT).resolve()
        canonical_main = _trusted_canonical_main(root)
        return evaluate_task_snapshot(
            task_id,
            repository_root=root,
            catalog_path=catalog_path,
            canonical_main=canonical_main,
        )
    '''
)
text = text[:eval_start] + eval_replacement.rstrip() + "\n"
gate.write_text(text, encoding="utf-8")

cli = Path("src/mstr_qualify/cli.py")
cli_text = cli.read_text(encoding="utf-8")
old_run = dedent(
    '''\
    def run_task_eligible(
        task_id: str,
        canonical_main: str,
    ) -> tuple[int, dict[str, Any]]:
        """Evaluate one task against an externally supplied current-main SHA."""

        result = evaluate_task_eligibility(task_id, canonical_main=canonical_main)
        exit_code = _EXIT_OK if result["eligible"] else _EXIT_FAIL_CLOSED
        return exit_code, result
    '''
)
new_run = dedent(
    '''\
    def run_task_eligible(task_id: str) -> tuple[int, dict[str, Any]]:
        """Evaluate one task against the verified canonical-main checkout."""

        result = evaluate_task_eligibility(task_id)
        exit_code = _EXIT_OK if result["eligible"] else _EXIT_FAIL_CLOSED
        return exit_code, result
    '''
)
cli_text = replace_once(cli_text, old_run, new_run, label="run_task_eligible")

parser_block = (
    '    task_eligible_parser.add_argument(\n'
    '        "--canonical-main",\n'
    '        required=True,\n'
    '        help="trusted exact current main SHA supplied by execution/merge governance",\n'
    '    )\n'
)
cli_text = replace_once(cli_text, parser_block, "", label="canonical-main parser")
cli_text = replace_once(
    cli_text,
    "            return run_task_eligible(args.task_id, args.canonical_main)\n",
    "            return run_task_eligible(args.task_id)\n",
    label="task dispatch",
)
cli.write_text(cli_text, encoding="utf-8")

integration = Path("tests/integration/test_task_gate_cli.py")
it = integration.read_text(encoding="utf-8")
for old_value, new_value, expected_count in (
    ("lambda task_id, *, canonical_main: expected", "lambda task_id: expected", 2),
    (
        'main(["task", "eligible", "B002", "--canonical-main", _CANONICAL_MAIN])',
        'main(["task", "eligible", "B002"])',
        1,
    ),
    (
        'main(["task", "eligible", "B003", "--canonical-main", _CANONICAL_MAIN])',
        'main(["task", "eligible", "B003"])',
        1,
    ),
    (
        "def fail_closed(task_id: str, *, canonical_main: str) -> dict[str, Any]:",
        "def fail_closed(task_id: str) -> dict[str, Any]:",
        1,
    ),
    (
        'main(["task", "eligible", "B999", "--canonical-main", _CANONICAL_MAIN])',
        'main(["task", "eligible", "B999"])',
        1,
    ),
):
    count = it.count(old_value)
    if count != expected_count:
        raise SystemExit(f"integration anchor mismatch for {old_value!r}: {count}")
    it = it.replace(old_value, new_value)

parser_old = (
    '    args = parser.parse_args(\n'
    '        ["task", "eligible", "B003", "--canonical-main", _CANONICAL_MAIN]\n'
    '    )\n\n'
    '    assert args.command == "task"\n'
    '    assert args.task_command == "eligible"\n'
    '    assert args.task_id == "B003"\n'
    '    assert args.canonical_main == _CANONICAL_MAIN\n'
)
parser_new = (
    '    args = parser.parse_args(["task", "eligible", "B003"])\n\n'
    '    assert args.command == "task"\n'
    '    assert args.task_command == "eligible"\n'
    '    assert args.task_id == "B003"\n'
    '    assert not hasattr(args, "canonical_main")\n'
)
it = replace_once(it, parser_old, parser_new, label="integration parser block")
it = it.rstrip() + dedent(
    '''

    def test_task_eligible_parser_rejects_caller_supplied_main() -> None:
        from mstr_qualify.cli import build_parser

        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["task", "eligible", "B003", "--canonical-main", "a" * 40])
    '''
) + "\n"
integration.write_text(it, encoding="utf-8")

contract = Path("tests/contract/test_task_gate.py")
ct = contract.read_text(encoding="utf-8")
test_start = ct.index("def test_real_evaluation_requires_trusted_current_main(tmp_path: Path) -> None:\n")
test_end = ct.index(
    "\ndef test_undeclared_not_required_state_cannot_satisfy_predecessor",
    test_start,
)
test_replacement = dedent(
    '''\
    def test_real_evaluation_requires_verified_main_refs(tmp_path: Path) -> None:
        catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
        _git(tmp_path, "init", "-b", "main")
        _git(tmp_path, "config", "user.name", "B002 Test")
        _git(tmp_path, "config", "user.email", "b002@example.invalid")
        _git(tmp_path, "add", ".")
        _git(tmp_path, "commit", "-m", "fixture main")
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        _git(tmp_path, "update-ref", "refs/remotes/origin/main", head)

        result = evaluate_task_eligibility(
            "B002",
            repository_root=tmp_path,
            catalog_path=catalog_path,
        )
        assert result["eligible"] is True
        assert result["canonical_main"] == head

        _git(tmp_path, "switch", "-c", "feature")
        (tmp_path / "feature.txt").write_text("feature\n", encoding="utf-8")
        _git(tmp_path, "add", "feature.txt")
        _git(tmp_path, "commit", "-m", "feature commit")
        with pytest.raises(QualificationError) as feature:
            evaluate_task_eligibility(
                "B002",
                repository_root=tmp_path,
                catalog_path=catalog_path,
            )
        assert feature.value.code == "task_gate.not_canonical_main"

        _git(tmp_path, "switch", "main")
        with catalog_path.open("a", encoding="utf-8") as handle:
            handle.write("\n")
        with pytest.raises(QualificationError) as dirty:
            evaluate_task_eligibility(
                "B002",
                repository_root=tmp_path,
                catalog_path=catalog_path,
            )
        assert dirty.value.code == "task_gate.dirty_checkout"


    def test_real_evaluation_rejects_main_tracking_ref_drift(tmp_path: Path) -> None:
        catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
        _git(tmp_path, "init", "-b", "main")
        _git(tmp_path, "config", "user.name", "B002 Test")
        _git(tmp_path, "config", "user.email", "b002@example.invalid")
        _git(tmp_path, "add", ".")
        _git(tmp_path, "commit", "-m", "fixture main")
        first_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        _git(tmp_path, "update-ref", "refs/remotes/origin/main", first_head)

        (tmp_path / "main-drift.txt").write_text("drift\n", encoding="utf-8")
        _git(tmp_path, "add", "main-drift.txt")
        _git(tmp_path, "commit", "-m", "local main drift")

        with pytest.raises(QualificationError) as drift:
            evaluate_task_eligibility(
                "B002",
                repository_root=tmp_path,
                catalog_path=catalog_path,
            )
        assert drift.value.code == "task_gate.main_ref_mismatch"
    '''
)
ct = ct[:test_start] + test_replacement.rstrip() + "\n" + ct[test_end:]
contract.write_text(ct, encoding="utf-8")
