from __future__ import annotations

import re
from pathlib import Path


def replace_once(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    assert count == 1
    return updated


def main() -> None:
    path = Path("tests/contract/test_task_gate.py")
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        r"def test_exact_founder_authority_unblocks_pending_b011\(\) -> None:\n.*?\n\ndef test_terminal_task_is_not_execution_eligible",
        """def test_exact_founder_authority_remains_bound_after_b011_closeout() -> None:\n    result = evaluate_task_snapshot(\"B011\", canonical_main=_CANONICAL_MAIN)\n\n    assert result[\"eligible\"] is False\n    assert result[\"state_consistency_result\"][\"observed_state\"] == \"COMPLETE_CANONICAL\"\n    assert \"task.already_terminal\" in result[\"reasons\"]\n    assert result[\"authority_result\"][\"authority_id\"] == (\n        \"B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED\"\n    )\n    assert result[\"authority_result\"][\"satisfied\"] is True\n\n\ndef test_terminal_task_is_not_execution_eligible""",
    )

    text = replace_once(
        text,
        r"def test_b011_weight_access_observes_exact_authority_after_b010_resolution\(\) -> None:\n.*?\n\ndef _symlink_or_skip",
        """def test_b011_weight_access_closeout_preserves_exact_authority_identity() -> None:\n    catalog = load_task_catalog()\n    node = catalog.nodes[\"B011\"]\n    assert node[\"canonical_state\"] == \"COMPLETE_CANONICAL\"\n    assert node[\"external_effect_class\"] == \"MODEL_WEIGHT_ACCESS\"\n    assert node[\"required_authority_id\"] == \"B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED\"\n    result = evaluate_task_snapshot(\"B011\", canonical_main=_CANONICAL_MAIN)\n    assert result[\"eligible\"] is False\n    assert \"task.already_terminal\" in result[\"reasons\"]\n    assert result[\"authority_result\"][\"required\"] is True\n    assert result[\"authority_result\"][\"satisfied\"] is True\n\n\ndef _symlink_or_skip""",
    )

    text = replace_once(
        text,
        r"def test_b014_closeout_does_not_change_b011_exact_authority_identity\(\) -> None:\n.*?\n\ndef test_b021_is_terminal_after_canonical_closeout",
        """def test_b014_and_b011_closeouts_preserve_b011_exact_authority_identity() -> None:\n    result = evaluate_task_snapshot(\"B011\", canonical_main=_CANONICAL_MAIN)\n\n    assert result[\"eligible\"] is False\n    assert result[\"state_consistency_result\"][\"observed_state\"] == \"COMPLETE_CANONICAL\"\n    assert result[\"authority_result\"][\"required\"] is True\n    assert result[\"authority_result\"][\"satisfied\"] is True\n    assert result[\"authority_result\"][\"authority_id\"] == \"B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED\"\n    assert \"task.already_terminal\" in result[\"reasons\"]\n    validate_instance(\"mstr-task-eligibility-v0\", result)\n\n\ndef test_b021_is_terminal_after_canonical_closeout""",
    )

    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
