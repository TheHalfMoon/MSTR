from __future__ import annotations

from pathlib import Path

PATH = Path("src/mstr_qualify/schemas.py")


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one occurrence, found {count}: {old}")
    return text.replace(old, new)


text = PATH.read_text(encoding="utf-8")
text = replace_once(
    text,
    '''    for field, expected in (
        ("governing_task_id", task_id),
        ("campaign_id", campaign_id),
        ("fidelity_level", level),
        ("frozen_evaluation_identity", evaluation_id),
    ):
        if policy.get(field) != expected:
            errors.append(f"$.promotion_policy_identity: policy {field} must match experiment")
''',
    '''    for field, expected_policy_value in (
        ("governing_task_id", task_id),
        ("campaign_id", campaign_id),
        ("fidelity_level", level),
        ("frozen_evaluation_identity", evaluation_id),
    ):
        if policy.get(field) != expected_policy_value:
            errors.append(f"$.promotion_policy_identity: policy {field} must match experiment")
''',
)
text = replace_once(
    text,
    '''        for field, expected in (
            ("governing_task_id", task_id),
            ("campaign_id", campaign_id),
            ("experiment_id", experiment_id),
            ("gate_id", gate_id),
        ):
            if evidence_record.get(field) != expected:
                errors.append(f"$.hard_gate_results[{index}]: gate evidence {field} must match experiment")
''',
    '''        for field, expected_evidence_value in (
            ("governing_task_id", task_id),
            ("campaign_id", campaign_id),
            ("experiment_id", experiment_id),
            ("gate_id", gate_id),
        ):
            if evidence_record.get(field) != expected_evidence_value:
                errors.append(f"$.hard_gate_results[{index}]: gate evidence {field} must match experiment")
''',
)
PATH.write_text(text, encoding="utf-8")
