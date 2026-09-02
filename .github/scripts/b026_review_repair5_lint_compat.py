from __future__ import annotations

from pathlib import Path

path = Path("src/mstr_qualify/schemas.py")
text = path.read_text(encoding="utf-8")

replacements = {
    '                            "$.hard_gate_results[universal_laptop_product_gates].evidence_identity: "\n': '                            "$.hard_gate_results[universal_laptop_product_gates]."\n                            "evidence_identity: "\n',
    '                        "$.q4_candidate_binding_identity_or_na: canonical Q4 candidate binding missing"\n': '                        "$.q4_candidate_binding_identity_or_na: canonical Q4 candidate "\n                        "binding missing"\n',
    '                            "$.q4_candidate_binding_identity_or_na: binding content address mismatch"\n': '                            "$.q4_candidate_binding_identity_or_na: binding content "\n                            "address mismatch"\n',
    '                            "$.q4_candidate_binding_identity_or_na: binding fields are not canonical"\n': '                            "$.q4_candidate_binding_identity_or_na: binding fields are "\n                            "not canonical"\n',
    '                            "$.q4_candidate_binding_identity_or_na: unsupported binding schema_version"\n': '                            "$.q4_candidate_binding_identity_or_na: unsupported binding "\n                            "schema_version"\n',
    '                            "$.q4_candidate_binding_identity_or_na: binding must reference resolved Q4 record"\n': '                            "$.q4_candidate_binding_identity_or_na: binding must reference "\n                            "resolved Q4 record"\n',
    '                            "$.q4_candidate_binding_identity_or_na: model_id must match promoted result"\n': '                            "$.q4_candidate_binding_identity_or_na: model_id must match "\n                            "promoted result"\n',
    '                            "$.q4_candidate_binding_identity_or_na: model_revision must match promoted result"\n': '                            "$.q4_candidate_binding_identity_or_na: model_revision must "\n                            "match promoted result"\n',
    '                            "$.q4_candidate_binding_identity_or_na: source checkpoint must match Q4 record"\n': '                            "$.q4_candidate_binding_identity_or_na: source checkpoint must "\n                            "match Q4 record"\n',
    '                            "$.q4_candidate_binding_identity_or_na: artifact must match promoted result"\n': '                            "$.q4_candidate_binding_identity_or_na: artifact must match "\n                            "promoted result"\n',
    '                "$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence"\n': '                "$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 "\n                "promotion evidence"\n',
    '                "$.q4_candidate_binding_identity_or_na: only L4 PROMOTE may bind Q4 candidate lineage"\n': '                "$.q4_candidate_binding_identity_or_na: only L4 PROMOTE may bind Q4 "\n                "candidate lineage"\n',
    '                        "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: positive network model/teacher "\n': '                        "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: positive "\n                        "network model/teacher "\n',
    '            "$.governed_effects.MODEL_EXECUTION: true declaration requires positive execution evidence"\n': '            "$.governed_effects.MODEL_EXECUTION: true declaration requires positive "\n            "execution evidence"\n',
    '            "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: true declaration requires positive call evidence"\n': '            "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: true declaration requires "\n            "positive call evidence"\n',
}

for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one lint target, found {count}: {old!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
