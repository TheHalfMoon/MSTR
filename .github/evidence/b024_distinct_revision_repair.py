from __future__ import annotations

from pathlib import Path


def patch_semantics() -> None:
    path = Path("src/mstr_qualify/schemas.py")
    text = path.read_text(encoding="utf-8")
    needle = '''    if isinstance(patch, dict) and isinstance(proof, dict):
        artifact_sha = patch.get("test_artifact_sha256")
'''
    replacement = '''    if isinstance(patch, dict) and isinstance(proof, dict):
        artifact_sha = patch.get("test_artifact_sha256")
        if (
            proof.get("proof_kind") == "FAIL_BEFORE_PASS_AFTER"
            and instance.get("base_revision") == instance.get("fix_revision")
        ):
            errors.append(
                "$.fix_revision: FAIL_BEFORE_PASS_AFTER requires a revision distinct from base_revision"
            )
'''
    if needle not in text:
        raise SystemExit("semantic insertion point not found")
    path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")


def patch_tests() -> None:
    path = Path("tests/contract/test_test_generation_example_contract.py")
    text = path.read_text(encoding="utf-8")
    marker = "\ndef test_b024_schema_has_no_remote_reference() -> None:\n"
    addition = '''

def test_b024_fail_before_pass_after_requires_distinct_revisions() -> None:
    value = fixture()
    value["fix_revision"] = value["base_revision"]
    proof = value["behavioral_proof"]
    assert isinstance(proof, dict)
    post = proof["post_fix_result"]
    assert isinstance(post, dict)
    post["revision"] = value["base_revision"]

    errors = validation_errors("mstr-test-generation-example-v0", value)
    assert any("requires a revision distinct from base_revision" in error for error in errors)
'''
    if "test_b024_fail_before_pass_after_requires_distinct_revisions" not in text:
        if marker not in text:
            raise SystemExit("test insertion point not found")
        text = text.replace(marker, addition + marker, 1)
    path.write_text(text, encoding="utf-8")


def patch_docs() -> None:
    path = Path("docs/data/TEST_GENERATION_CURRICULUM.md")
    text = path.read_text(encoding="utf-8")
    needle = "PRE_FIX_REVISION = BASE_REVISION\nPOST_FIX_REVISION = FIX_REVISION\n"
    replacement = (
        "PRE_FIX_REVISION = BASE_REVISION\n"
        "POST_FIX_REVISION = FIX_REVISION\n"
        "BASE_REVISION != FIX_REVISION\n"
    )
    if needle not in text:
        raise SystemExit("curriculum proof block not found")
    text = text.replace(needle, replacement, 1)
    rejected = "- pass both before and after under `FAIL_BEFORE_PASS_AFTER`;\n"
    text = text.replace(
        rejected,
        rejected
        + "- claim a repair while `base_revision` and `fix_revision` are identical;\n",
        1,
    )
    path.write_text(text, encoding="utf-8")

    path = Path("evidence/mstr-000b/B024-test-curriculum.md")
    text = path.read_text(encoding="utf-8")
    needle = "SAME_VERIFIER_MANIFEST_PRE_POST = required\n"
    if needle not in text:
        raise SystemExit("evidence contract block not found")
    text = text.replace(
        needle,
        needle + "FAIL_BEFORE_PASS_AFTER_DISTINCT_BASE_FIX_REVISIONS = required\n",
        1,
    )
    remediation = '''

### Distinct-revision review remediation

The initial Codex review also identified that `FAIL_BEFORE_PASS_AFTER` could describe contradictory fail/pass outcomes on an identical code revision. This repair requires `base_revision != fix_revision` for that proof kind and adds a regression test that reproduces the rejected identical-revision case. `TASK_SPECIFIC_BEHAVIOR` is unchanged because this restriction is specific to claimed repair transitions.
'''
    if "### Distinct-revision review remediation" not in text:
        text += remediation
    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch_semantics()
    patch_tests()
    patch_docs()


if __name__ == "__main__":
    main()
