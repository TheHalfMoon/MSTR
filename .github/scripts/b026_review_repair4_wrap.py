from __future__ import annotations

from pathlib import Path

PATH = Path("src/mstr_qualify/schemas.py")


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one occurrence, found {count}: {old}")
    return text.replace(old, new)


text = PATH.read_text(encoding="utf-8")
replacements = [
    (
        'f"$.hard_gate_results[{index}].status: submitted status does not match predeclared criterion"',
        'f"$.hard_gate_results[{index}].status: submitted status does not match "\n'
        '                "predeclared criterion"',
    ),
    (
        '"$.q4_promotion_record_identity_or_na: L4 PROMOTE requires a sha256-bound Q4 record"',
        '"$.q4_promotion_record_identity_or_na: L4 PROMOTE requires a "\n'
        '                    "sha256-bound Q4 record"',
    ),
    (
        '"$.q4_promotion_record_identity_or_na: immutable Q4 promotion record missing"',
        '"$.q4_promotion_record_identity_or_na: immutable Q4 promotion "\n'
        '                        "record missing"',
    ),
    (
        '"$.q4_promotion_record_identity_or_na: Q4 record content address mismatch"',
        '"$.q4_promotion_record_identity_or_na: Q4 record content address "\n'
        '                            "mismatch"',
    ),
    (
        '"$.q4_promotion_record_identity_or_na: referenced Q4 promotion record is invalid"',
        '"$.q4_promotion_record_identity_or_na: referenced Q4 promotion record "\n'
        '                            "is invalid"',
    ),
    (
        '"$.q4_promotion_record_identity_or_na: referenced Q4 record must be PROMOTED"',
        '"$.q4_promotion_record_identity_or_na: referenced Q4 record must be "\n'
        '                            "PROMOTED"',
    ),
    (
        '"$.q4_promotion_record_identity_or_na: Q4 record artifact must match promoted result"',
        '"$.q4_promotion_record_identity_or_na: Q4 record artifact must match "\n'
        '                            "promoted result"',
    ),
    (
        '"$.q4_promotion_record_identity_or_na: L4 requires universal-laptop gate PASS"',
        '"$.q4_promotion_record_identity_or_na: L4 requires universal-laptop "\n'
        '                            "gate PASS"',
    ),
    (
        '"$.hard_gate_results[universal_laptop_product_gates].evidence_identity: "',
        '"$.hard_gate_results[universal_laptop_product_gates]."\n'
        '                            "evidence_identity: "',
    ),
]
for old, new in replacements:
    text = replace_once(text, old, new)
PATH.write_text(text, encoding="utf-8")
