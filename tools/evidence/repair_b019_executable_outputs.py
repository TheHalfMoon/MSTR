from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()


def repo_path(relative: str) -> Path:
    return ROOT / relative


schema_paths = [
    repo_path("schemas/mstr-teacher-rescue-record-v0.schema.json"),
    repo_path(
        "specs/002-code-model-supremacy-foundation/contracts/"
        "mstr-teacher-rescue-record-v0.schema.json"
    ),
]

for schema_path in schema_paths:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    output = schema["$defs"]["teacher_output"]
    if "allOf" in output:
        raise SystemExit(f"unexpected existing teacher_output allOf in {schema_path}")
    output["allOf"] = [
        {
            "if": {
                "properties": {
                    "output_kind": {"enum": ["SOLUTION", "TEST"]},
                },
                "required": ["output_kind"],
            },
            "then": {
                "properties": {
                    "execution_required": {"const": True},
                }
            },
        }
    ]
    schema_path.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

policy = repo_path("docs/data/TEACHER_RESCUE_POLICY.md")
policy_text = policy.read_text(encoding="utf-8")
policy_old = (
    "Independent execution evidence must exactly cover outputs marked "
    "`execution_required=true`."
)
policy_new = (
    policy_old
    + " `SOLUTION` and `TEST` outputs are execution-required by contract and "
    "cannot opt out of independent execution."
)
if policy_text.count(policy_old) != 1:
    raise SystemExit("policy execution-rule anchor mismatch")
policy.write_text(policy_text.replace(policy_old, policy_new), encoding="utf-8")

evidence = repo_path("evidence/mstr-000b/B019-teacher-policy.md")
evidence_text = evidence.read_text(encoding="utf-8")
evidence_old = (
    "Teacher identity is not truth. Teacher terms are not concrete-output rights. "
    "Missing/unresolved provenance, rights, contamination, required execution, "
    "or verifier independence fails closed."
)
evidence_new = (
    evidence_old
    + " `SOLUTION` and `TEST` outputs cannot declare execution optional."
)
if evidence_text.count(evidence_old) != 1:
    raise SystemExit("evidence execution-rule anchor mismatch")
evidence.write_text(
    evidence_text.replace(evidence_old, evidence_new),
    encoding="utf-8",
)

tests = repo_path("tests/contract/test_teacher_rescue_contract.py")
test_text = tests.read_text(encoding="utf-8")
anchor = '''def test_b019_required_execution_must_be_independently_bound() -> None:
    value = fixture()
    value["independent_execution_results"] = []
    assert any("execution-required teacher output ids" in item for item in errors(value))


'''
addition = '''def test_b019_solution_and_test_outputs_cannot_opt_out_of_execution() -> None:
    for output_kind in ("SOLUTION", "TEST"):
        value = fixture()
        value["teacher_outputs"][0]["output_kind"] = output_kind
        value["teacher_outputs"][0]["execution_required"] = False
        value["independent_execution_results"] = []
        assert errors(value)


'''
if test_text.count(anchor) != 1:
    raise SystemExit("teacher-rescue test anchor mismatch")
tests.write_text(test_text.replace(anchor, anchor + addition), encoding="utf-8")
