from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


runtime_path = "schemas/mstr-teacher-rescue-record-v0.schema.json"
design_path = (
    "specs/002-code-model-supremacy-foundation/contracts/"
    "mstr-teacher-rescue-record-v0.schema.json"
)
runtime_bytes = (ROOT / runtime_path).read_bytes()
design_bytes = (ROOT / design_path).read_bytes()
assert runtime_bytes == design_bytes
schema = json.loads(runtime_bytes)

assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
assert schema["$id"] == "https://mstr.local/schemas/mstr-teacher-rescue-record-v0.json"
assert schema["properties"]["schema_version"]["const"] == "mstr.teacher-rescue-record.v0"

required = set(schema["required"])
assert {
    "rescue_id",
    "task_identity",
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
execution_rule = teacher_output["allOf"][0]
assert set(execution_rule["if"]["properties"]["output_kind"]["enum"]) == {
    "SOLUTION",
    "TEST",
}
assert execution_rule["then"]["properties"]["execution_required"]["const"] is True

admit_rules = None
for rule in schema["allOf"]:
    if rule.get("if", {}).get("properties", {}).get("admission_decision", {}).get("const") == "ADMIT":
        admit_rules = rule["then"]["properties"]
        break
assert admit_rules is not None
assert admit_rules["contamination_status"]["const"] == "CLEAR"
assert admit_rules["admission_reasons"]["maxItems"] == 0
assert (
    admit_rules["output_provenance"]["items"]["properties"]["provenance"]
    ["properties"]["lineage_status"]["const"]
    == "COMPLETE"
)
assert (
    admit_rules["output_rights_decisions"]["items"]["properties"]["rights_decision"]
    ["properties"]["decision"]["const"]
    == "COMPATIBLE"
)
assert (
    admit_rules["independent_execution_results"]["items"]["properties"]["sandboxed"]["const"]
    is True
)
assert (
    admit_rules["independent_execution_results"]["items"]["properties"]["result"]["const"]
    == "PASS"
)
verifier_admit = admit_rules["verifier_health"]["properties"]
assert verifier_admit["health_class"]["const"] == "HEALTHY"
assert verifier_admit["independence"]["const"] == "INDEPENDENT"
assert verifier_admit["teacher_output_sole_authority"]["const"] is False

cost = schema["properties"]["cost_record"]["properties"]
assert cost["paid_cost_usd"]["minimum"] == 0
assert cost["network_used"]["type"] == "boolean"
assert cost["model_execution_occurred"]["type"] == "boolean"
authority_shapes = cost["external_effect_authority_identity"]["anyOf"]
assert any(item.get("type") == "string" for item in authority_shapes)
assert any(item.get("type") == "null" for item in authority_shapes)

schemas_py = read("src/mstr_qualify/schemas.py")
for phrase in (
    "bindings must exactly cover teacher output ids",
    "bindings must exactly cover execution-required teacher output ids",
    "required when paid cost, network use, or model execution is recorded",
    "must be null when no external effect is recorded",
    "REFERENCE_ONLY cannot record paid cost, network use, or model execution",
    "REMOTE_API requires recorded network use and model execution",
    "LOCAL_MODEL requires recorded model execution",
):
    assert phrase in schemas_py

policy = read("docs/data/TEACHER_RESCUE_POLICY.md")
evidence = read("evidence/mstr-000b/B019-teacher-policy.md")
tests = read("tests/contract/test_teacher_rescue_contract.py")
for text in (policy, evidence):
    for phrase in (
        "MODEL_EXECUTION = NONE",
        "PAID_MODEL_API = NONE",
        "WEIGHT_CHANGING_TRAINING = NONE",
        "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE",
        "B022_VERIFIER_HEALTH_AUTHORITY = NONE",
    ):
        assert phrase in text
assert "does not create or widen that authority" in policy
assert "SOLUTION` and `TEST` outputs are execution-required" in policy
assert "SOLUTION` and `TEST` outputs cannot declare execution optional" in evidence
assert "test_b019_solution_and_test_outputs_cannot_opt_out_of_execution" in tests
assert "test_b019_external_effect_requires_existing_authority_identity" in tests
assert "test_b019_reference_only_cannot_claim_external_effect" in tests
assert "test_b019_remote_api_record_requires_network_and_execution_facts" in tests
assert "test_b019_zero_effect_record_rejects_spurious_authority_identity" in tests
