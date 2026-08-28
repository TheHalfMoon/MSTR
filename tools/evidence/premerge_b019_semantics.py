from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()

runtime = ROOT / "schemas/mstr-teacher-rescue-record-v0.schema.json"
design = (
    ROOT
    / "specs/002-code-model-supremacy-foundation/contracts/"
    / "mstr-teacher-rescue-record-v0.schema.json"
)
assert runtime.read_bytes() == design.read_bytes()
schema = json.loads(runtime.read_text(encoding="utf-8"))
assert schema["properties"]["schema_version"]["const"] == "mstr.teacher-rescue-record.v0"

required = set(schema["required"])
assert {
    "student_failure_evidence",
    "teacher_identity",
    "teacher_terms_identity",
    "cost_record",
    "teacher_outputs",
    "output_provenance",
    "output_rights_decisions",
    "contamination_status",
    "independent_execution_results",
    "verifier_health",
    "admission_decision",
    "admission_reasons",
} <= required

teacher_output = schema["$defs"]["teacher_output"]
mandatory_exec = teacher_output["allOf"][0]
assert set(mandatory_exec["if"]["properties"]["output_kind"]["enum"]) == {
    "SOLUTION",
    "TEST",
}
assert mandatory_exec["then"]["properties"]["execution_required"]["const"] is True

admit = next(
    rule["then"]["properties"]
    for rule in schema["allOf"]
    if rule.get("if", {}).get("properties", {}).get("admission_decision", {}).get("const")
    == "ADMIT"
)
assert admit["contamination_status"]["const"] == "CLEAR"
assert admit["admission_reasons"]["maxItems"] == 0
assert (
    admit["output_provenance"]["items"]["properties"]["provenance"]
    ["properties"]["lineage_status"]["const"]
    == "COMPLETE"
)
assert (
    admit["output_rights_decisions"]["items"]["properties"]["rights_decision"]
    ["properties"]["decision"]["const"]
    == "COMPATIBLE"
)
assert admit["independent_execution_results"]["items"]["properties"]["sandboxed"]["const"] is True
assert admit["independent_execution_results"]["items"]["properties"]["result"]["const"] == "PASS"
assert admit["verifier_health"]["properties"]["health_class"]["const"] == "HEALTHY"
assert admit["verifier_health"]["properties"]["independence"]["const"] == "INDEPENDENT"
assert admit["verifier_health"]["properties"]["teacher_output_sole_authority"]["const"] is False

schemas_py = (ROOT / "src/mstr_qualify/schemas.py").read_text(encoding="utf-8")
for fragment in (
    "bindings must exactly cover teacher output ids",
    "execution-required teacher output ids",
    "external_effect_authority_identity",
    "paid cost, network use, or model execution is recorded",
    "no external effect is recorded",
    "REFERENCE_ONLY cannot record ",
    "REMOTE_API requires recorded ",
    "LOCAL_MODEL requires recorded ",
):
    assert fragment in schemas_py

policy = (ROOT / "docs/data/TEACHER_RESCUE_POLICY.md").read_text(encoding="utf-8")
evidence = (ROOT / "evidence/mstr-000b/B019-teacher-policy.md").read_text(encoding="utf-8")
for text in (policy, evidence):
    for phrase in (
        "MODEL_WEIGHT_ACCESS = NONE",
        "MODEL_EXECUTION = NONE",
        "PAID_MODEL_API = NONE",
        "WEIGHT_CHANGING_TRAINING = NONE",
        "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE",
        "B022_VERIFIER_HEALTH_AUTHORITY = NONE",
    ):
        assert phrase in text
