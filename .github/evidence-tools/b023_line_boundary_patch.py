from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    assert count == 1, (old, count)
    return text.replace(old, new, 1)


source_path = Path("src/mstr_qualify/task_gate.py")
source = source_path.read_text(encoding="utf-8")
old = '''    for line in text.splitlines(keepends=True):\n        logical = line.rstrip("\\r\\n")\n        if fence_char is None:\n            match = opener.match(logical)\n            if match is None:\n                visible.append(line)\n                continue\n            fence = match.group("fence")\n            fence_char = fence[0]\n            fence_length = len(fence)\n            continue\n\n        match = closer.match(logical)\n        if (\n            match is not None\n            and match.group("fence")[0] == fence_char\n            and len(match.group("fence")) >= fence_length\n        ):\n            fence_char = None\n            fence_length = 0\n\n    return "".join(visible)\n'''
new = '''    for logical in text.splitlines():\n        if fence_char is None:\n            match = opener.match(logical)\n            if match is None:\n                visible.append(logical)\n                continue\n            fence = match.group("fence")\n            fence_char = fence[0]\n            fence_length = len(fence)\n            continue\n\n        match = closer.match(logical)\n        if (\n            match is not None\n            and match.group("fence")[0] == fence_char\n            and len(match.group("fence")) >= fence_length\n        ):\n            fence_char = None\n            fence_length = 0\n\n    return "\\n".join(visible)\n'''
source = replace_once(source, old, new)
source_path.write_text(source, encoding="utf-8")


tests_path = Path("tests/contract/test_task_gate.py")
tests = tests_path.read_text(encoding="utf-8")
marker = "test_external_prerequisite_splitlines_boundary_duplicate_rows_fail_closed"
assert marker not in tests

tests += r'''


_SPLITLINES_NON_CRLF_BOUNDARIES = [
    "\v",
    "\f",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x85",
    "\u2028",
    "\u2029",
]


@pytest.mark.parametrize("separator", _SPLITLINES_NON_CRLF_BOUNDARIES)
def test_external_prerequisite_splitlines_boundary_duplicate_rows_fail_closed(
    tmp_path: Path,
    separator: str,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = (
        tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    )
    external_tasks.write_text(
        f"- [x] **A006 Canonical row.**{separator}"
        "- [ ] **A006 Conflicting duplicate.**",
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


@pytest.mark.parametrize("separator", _SPLITLINES_NON_CRLF_BOUNDARIES)
def test_external_prerequisite_splitlines_boundary_fence_closes_before_canonical_row(
    tmp_path: Path,
    separator: str,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = (
        tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    )
    external_tasks.write_text(
        f"```{separator}"
        f"- [ ] **A006 Fenced example.**{separator}"
        f"```{separator}"
        "- [x] **A006 Canonical row.**",
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is True
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []
'''
tests_path.write_text(tests, encoding="utf-8")


evidence_path = Path("evidence/mstr-000b/B023-cross-workstream-binding-reconciliation.md")
evidence = evidence_path.read_text(encoding="utf-8")
heading = "## Universal logical-line boundary normalization from independent review"
assert heading not in evidence
evidence += r'''

## Universal logical-line boundary normalization from independent review

Independent exact-head review of PR #131 found that the external checklist title matcher excluded only CR/LF while the fenced-Markdown helper used Python `splitlines()`, whose logical-line boundary set also includes vertical tab, form feed, record/group/file separators, NEL, and Unicode line/paragraph separators. Because the helper rejoined visible text with the original separators, a checked checklist row and a contradictory duplicate separated by one of those boundaries could be consumed as one regex record. The helper now parses with `splitlines()` without retaining boundary bytes and rejoins visible logical lines using canonical LF. All downstream external Markdown matching therefore observes the same line model used by the fence parser. Parameterized regressions cover every non-CR/LF boundary recognized by Python `splitlines()`: `\v`, `\f`, `\x1c`, `\x1d`, `\x1e`, `\x85`, `U+2028`, and `U+2029`. Contradictory duplicate checklist rows remain unverifiable, while fenced examples close correctly before a canonical row. No external authority or B023 completion state is created by this parser hardening.
'''
evidence_path.write_text(evidence, encoding="utf-8")
