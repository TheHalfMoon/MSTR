from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, needle: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(needle)
    if count != 1:
        raise SystemExit(f"{path}: target must occur exactly once; observed={count}")
    path.write_text(text.replace(needle, replacement), encoding="utf-8")


def patch_schemas() -> None:
    path = Path("src/mstr_qualify/schemas.py")
    needle = '''                expected_binding = (
                    _task_specific_acceptance_binding(
                        instance,
                        patch,
                        post,
                        evidence_identity,
                    )
                    if evidence_identity is not None
                    else None
                )
                if raw_binding != expected_binding:
'''
    replacement = '''                expected_binding = (
                    _task_specific_acceptance_binding(
                        instance,
                        patch,
                        post,
                        evidence_identity,
                    )
                    if evidence_identity is not None
                    else None
                )
                execution_evidence_identities = {
                    value
                    for value in (
                        pre.get("evidence_identity"),
                        post.get("evidence_identity"),
                    )
                    if isinstance(value, str)
                }
                if (
                    evidence_identity is not None
                    and evidence_identity in execution_evidence_identities
                ):
                    errors.append(
                        "$.behavioral_proof.independent_acceptance_evidence_identity: "
                        "TASK_SPECIFIC_BEHAVIOR independent acceptance evidence must be "
                        "distinct from pre/post execution evidence identities"
                    )
                if raw_binding != expected_binding:
'''
    replace_once(path, needle, replacement)


def patch_tests() -> None:
    path = Path("tests/contract/test_test_generation_example_contract.py")
    anchor = "\ndef test_b024_mutation_accounting_and_strength_fail_closed() -> None:\n"
    regression = '''
def test_b024_task_specific_independent_evidence_cannot_reuse_execution_evidence() -> None:
    for source in ("pre_fix_result", "post_fix_result"):
        value = task_specific_fixture()
        proof = value["behavioral_proof"]
        patch = value["generated_test_patch"]
        assert isinstance(proof, dict)
        assert isinstance(patch, dict)
        post = proof["post_fix_result"]
        result = proof[source]
        assert isinstance(post, dict)
        assert isinstance(result, dict)
        evidence_identity = result["evidence_identity"]
        assert isinstance(evidence_identity, str)
        payload = {
            "environment_identity": post["environment_identity"],
            "execution_evidence_identity": post["evidence_identity"],
            "independent_acceptance_evidence_identity": evidence_identity,
            "revision": value["fix_revision"],
            "task_identity": value["task_identity"],
            "test_artifact_sha256": patch["test_artifact_sha256"],
            "verifier_manifest_id": post["verifier_manifest_id"],
        }
        encoded = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        proof["independent_acceptance_evidence_identity"] = (
            f"{evidence_identity}|binding-sha256:{hashlib.sha256(encoded).hexdigest()}"
        )
        errors = validation_errors("mstr-test-generation-example-v0", value)
        assert any(
            "independent acceptance evidence must be distinct from pre/post "
            "execution evidence identities" in error
            for error in errors
        )

'''
    replace_once(path, anchor, regression + anchor)


def patch_evidence() -> None:
    path = Path("evidence/mstr-000b/B024-test-curriculum.md")
    text = path.read_text(encoding="utf-8")
    marker = "TASK_SPECIFIC_ACCEPTANCE_INDEPENDENT_FROM_EXECUTION_EVIDENCE = required"
    if marker in text:
        raise SystemExit(f"{path}: marker already exists unexpectedly")
    text += '''

## Exact-head independent-evidence hardening

Fresh independent review proved that a task-specific acceptance identity must not reuse either pre-fix or post-fix execution evidence and merely recompute the context digest. Semantic admission now requires the independent identity to be distinct from both execution-evidence identities while preserving the existing exact-context SHA-256 binding.

```text
TASK_SPECIFIC_ACCEPTANCE_INDEPENDENT_FROM_EXECUTION_EVIDENCE = required
```
'''
    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch_schemas()
    patch_tests()
    patch_evidence()


if __name__ == "__main__":
    main()
