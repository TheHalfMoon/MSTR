from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    assert count == 1, (old, count)
    return text.replace(old, new, 1)


source_path = Path("src/mstr_qualify/task_gate.py")
source = source_path.read_text(encoding="utf-8")
for old, new in (
    (
        r'''    opener = re.compile(r"^[ \\t]{0,3}(?P<fence>`{3,}|~{3,})")''',
        r'''    opener = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")''',
    ),
    (
        r'''    closer = re.compile(r"^[ \\t]{0,3}(?P<fence>`{3,}|~{3,})[ \\t]*$")''',
        r'''    closer = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})[ \t]*$")''',
    ),
    (
        r'''        rf"^- \[(?P<mark>[ xX])\] \*\*{re.escape(task_id)}\s+[^\r\n]+?\*\*\s*$",''',
        r'''        rf"^- \[(?P<mark>[ xX])\] \*\*{re.escape(task_id)}[ \t]+[^\r\n]+?\*\*[ \t]*$",''',
    ),
    (
        r'''            r"^\*\*Task:\*\*\s*`(?P<task>[^`]+)`\s*$",''',
        r'''            r"^\*\*Task:\*\*[ \t]*`(?P<task>[^`\r\n]+)`[ \t]*$",''',
    ),
    (
        r'''            r"^\*\*State:\*\*\s*`(?P<state>[^`]+)`\s*$",''',
        r'''            r"^\*\*State:\*\*[ \t]*`(?P<state>[^`\r\n]+)`[ \t]*$",''',
    ),
):
    source = replace_once(source, old, new)
source_path.write_text(source, encoding="utf-8")


tests_path = Path("tests/contract/test_task_gate.py")
tests = tests_path.read_text(encoding="utf-8")
marker = "test_external_prerequisite_literal_t_fence_does_not_hide_duplicate_row"
assert marker not in tests

tests += r'''


def test_external_prerequisite_literal_t_fence_does_not_hide_duplicate_row(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = (
        tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    )
    external_tasks.write_text(
        "- [x] **A006 Canonical row.**\n"
        "t```\n"
        "- [ ] **A006 Conflicting duplicate.**\n",
        encoding="utf-8",
    )
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


def test_external_prerequisite_tab_indented_fence_still_hides_fenced_duplicate(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = (
        tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    )
    external_tasks.write_text(
        "- [x] **A006 Canonical row.**\n"
        "\t```\n"
        "- [ ] **A006 Fenced duplicate.**\n"
        "\t```\n",
        encoding="utf-8",
    )
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is True
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []


@pytest.mark.parametrize(
    ("tasks_text", "evidence_text", "expected_reason"),
    [
        (
            "- [x] **A006\nExternal task.**\n",
            "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
            "prerequisite.external_checkbox_unverifiable",
        ),
        (
            "- [x] **A006 External task.**\n",
            "**Task:**\n`MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
            "prerequisite.external_identity_unproven",
        ),
        (
            "- [x] **A006 External task.**\n",
            "**Task:** `MSTR-000A / A006`\n**State:**\n`COMPLETE_CANONICAL`\n",
            "prerequisite.external_state_unproven",
        ),
    ],
)
def test_external_prerequisite_newline_split_records_fail_closed(
    tmp_path: Path,
    tasks_text: str,
    evidence_text: str,
    expected_reason: str,
) -> None:
    catalog_path = _write_external_binding_fixture(tmp_path, evidence_text)
    external_tasks = (
        tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    )
    external_tasks.write_text(tasks_text, encoding="utf-8")
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is False
    assert predecessor["satisfied"] is False
    assert expected_reason in predecessor["reasons"]
'''
tests_path.write_text(tests, encoding="utf-8")


evidence_path = Path("evidence/mstr-000b/B023-cross-workstream-binding-reconciliation.md")
evidence = evidence_path.read_text(encoding="utf-8")
heading = "## Horizontal-whitespace parser hardening from independent review"
assert heading not in evidence
evidence += r'''

## Horizontal-whitespace parser hardening from independent review

Independent exact-head review of PR #130 found two fail-closed parser defects. First, the fenced-Markdown parser used a raw regex character class containing `\\t`, which matches a literal backslash or `t` instead of an actual tab; a literal `t``` marker could therefore start a false fence and suppress later duplicate or conflicting canonical records. Fence indentation now recognizes only spaces and actual tab escapes. Second, structured `Task` and `State` declarations used `\s*`, allowing malformed newline-split declarations to be interpreted as canonical records. Their optional whitespace is now horizontal-only and captured values are constrained to one line. The same horizontal-only rule is applied proactively to external checklist whitespace so a task id and title cannot be joined across a newline. Regressions cover literal `t``` markers, real tab-indented fences, newline-split checklist rows, and newline-split `Task` and `State` declarations. All malformed forms remain fail-closed.
'''
evidence_path.write_text(evidence, encoding="utf-8")
