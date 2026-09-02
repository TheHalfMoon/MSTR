from __future__ import annotations

from pathlib import Path

PATH = Path("src/mstr_qualify/schemas.py")
text = PATH.read_text(encoding="utf-8")

replacements = {
    '"$.hard_gate_results[universal_laptop_product_gates].evidence_identity: "': (
        '"$.hard_gate_results[universal_laptop_product_gates]." +\n'
        '                            "evidence_identity: "'
    ),
    '"$.q4_candidate_binding_identity_or_na: canonical Q4 candidate binding missing"': (
        '"$.q4_candidate_binding_identity_or_na: canonical Q4 " +\n'
        '                        "candidate binding missing"'
    ),
    '"$.q4_candidate_binding_identity_or_na: binding content address mismatch"': (
        '"$.q4_candidate_binding_identity_or_na: binding content " +\n'
        '                            "address mismatch"'
    ),
    '"$.q4_candidate_binding_identity_or_na: binding fields are not canonical"': (
        '"$.q4_candidate_binding_identity_or_na: binding fields are " +\n'
        '                            "not canonical"'
    ),
    '"$.q4_candidate_binding_identity_or_na: unsupported binding schema_version"': (
        '"$.q4_candidate_binding_identity_or_na: unsupported binding " +\n'
        '                            "schema_version"'
    ),
    '"$.q4_candidate_binding_identity_or_na: binding must reference resolved Q4 record"': (
        '"$.q4_candidate_binding_identity_or_na: binding must reference " +\n'
        '                            "resolved Q4 record"'
    ),
    '"$.q4_candidate_binding_identity_or_na: model_id must match promoted result"': (
        '"$.q4_candidate_binding_identity_or_na: model_id must match " +\n'
        '                            "promoted result"'
    ),
    '"$.q4_candidate_binding_identity_or_na: model_revision must match promoted result"': (
        '"$.q4_candidate_binding_identity_or_na: model_revision must " +\n'
        '                            "match promoted result"'
    ),
    '"$.q4_candidate_binding_identity_or_na: source checkpoint must match Q4 record"': (
        '"$.q4_candidate_binding_identity_or_na: source checkpoint must " +\n'
        '                            "match Q4 record"'
    ),
    '"$.q4_candidate_binding_identity_or_na: artifact must match promoted result"': (
        '"$.q4_candidate_binding_identity_or_na: artifact must match " +\n'
        '                            "promoted result"'
    ),
    '"$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence"': (
        '"$.q4_promotion_record_identity_or_na: only L4 PROMOTE may " +\n'
        '                "bind Q4 promotion evidence"'
    ),
    '"$.q4_candidate_binding_identity_or_na: only L4 PROMOTE may bind Q4 candidate lineage"': (
        '"$.q4_candidate_binding_identity_or_na: only L4 PROMOTE may " +\n'
        '                "bind Q4 candidate lineage"'
    ),
    '"$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: positive network model/teacher "': (
        '"$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: " +\n'
        '                        "positive network model/teacher "'
    ),
    '"$.governed_effects.MODEL_EXECUTION: true declaration requires positive execution evidence"': (
        '"$.governed_effects.MODEL_EXECUTION: true declaration requires " +\n'
        '            "positive execution evidence"'
    ),
    '"$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: true declaration requires positive call evidence"': (
        '"$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: true declaration " +\n'
        '            "requires positive call evidence"'
    ),
}

for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one occurrence of {old!r}, found {count}")
    text = text.replace(old, new, 1)

PATH.write_text(text, encoding="utf-8")
