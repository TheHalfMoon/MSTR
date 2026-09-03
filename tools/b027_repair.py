from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def repair_script(root: Path) -> None:
    path = root / "scripts" / "research" / "b027_ladder_pilot.py"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "from mstr_qualify.schemas import validate_instance\n",
        "from jsonschema import Draft202012Validator\n\n"
        "from mstr_qualify.schemas import load_schema, validate_instance\n",
        label="imports",
    )
    text = replace_once(
        text,
        'TASK_ID = "B027"\nCAMPAIGN_ID = "b027-offline-ladder-pilot-v0"\n',
        'TASK_ID = "B027"\n'
        'CAMPAIGN_ID = "b027-offline-ladder-pilot-v0"\n'
        'CANONICAL_ENTRY_MAIN = "312d40eee8400a0dab94633f891b206f66a82855"\n'
        '_CANONICAL_REFS = ("refs/heads/main", "refs/remotes/origin/main")\n',
        label="constants",
    )

    old_validation = '''def _set_local_main(sha: str) -> None:
    _git("update-ref", "refs/heads/main", sha)
    _git("update-ref", "refs/remotes/origin/main", sha)


def _validate_record(record: dict[str, Any], head_sha: str) -> None:
    _set_local_main(head_sha)
    validate_instance("mstr-research-experiment-v2", record, repository_root=ROOT)
'''
    new_validation = '''def _resolve_ref(ref: str) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else None


def _canonical_ref_snapshot() -> dict[str, str | None]:
    return {ref: _resolve_ref(ref) for ref in _CANONICAL_REFS}


def _require_trusted_canonical_entry(
    expected_sha: str = CANONICAL_ENTRY_MAIN,
) -> dict[str, str | None]:
    snapshot = _canonical_ref_snapshot()
    origin_main = snapshot["refs/remotes/origin/main"]
    local_main = snapshot["refs/heads/main"]
    if origin_main != expected_sha:
        raise RuntimeError(
            f"origin/main is not the trusted B027 canonical entry: {origin_main!r}"
        )
    if local_main is not None and local_main != expected_sha:
        raise RuntimeError(
            f"local main disagrees with the trusted B027 canonical entry: {local_main!r}"
        )
    return snapshot


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode not in {0, 1}:
        raise RuntimeError(
            f"unable to compare Git ancestry: {ancestor} -> {descendant}: "
            f"{completed.stderr.strip()}"
        )
    return completed.returncode == 0


def _is_strict_ancestor(ancestor: str, descendant: str) -> bool:
    return ancestor != descendant and _is_ancestor(ancestor, descendant)


def _validate_schema_shape(record: dict[str, Any]) -> None:
    schema = load_schema("mstr-research-experiment-v2")
    errors = sorted(
        Draft202012Validator(schema).iter_errors(record),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        joined = "; ".join(error.message for error in errors)
        raise RuntimeError(f"B027 candidate record schema validation failed: {joined}")


def _validate_record_candidate(record: dict[str, Any], head_sha: str) -> None:
    before = _require_trusted_canonical_entry()
    try:
        _validate_schema_shape(record)
        if not _is_ancestor(CANONICAL_ENTRY_MAIN, head_sha):
            raise RuntimeError("candidate head does not descend from canonical B027 entry")
        freeze_sha = record.get("campaign_freeze_commit_sha_or_na")
        evidence_sha = record.get("canonical_evidence_commit_sha_or_na")
        if not isinstance(freeze_sha, str) or len(freeze_sha) != 40:
            raise RuntimeError("candidate campaign freeze commit is not concrete")
        if not isinstance(evidence_sha, str) or len(evidence_sha) != 40:
            raise RuntimeError("candidate evidence commit is not concrete")
        if not _is_strict_ancestor(freeze_sha, evidence_sha):
            raise RuntimeError("candidate freeze must strictly precede evidence")
        if not _is_ancestor(evidence_sha, head_sha):
            raise RuntimeError("candidate evidence is not visible at candidate head")

        predecessor = record.get("predecessor_promotion")
        if isinstance(predecessor, dict):
            experiment_id = predecessor.get("experiment_id")
            expected_digest = predecessor.get("experiment_record_sha256")
            if not isinstance(experiment_id, str) or not isinstance(expected_digest, str):
                raise RuntimeError("candidate predecessor binding is incomplete")
            predecessor_path = RESULT_ROOT / "registry" / f"{experiment_id}.json"
            raw = predecessor_path.read_bytes()
            actual_digest = hashlib.sha256(raw).hexdigest()
            if actual_digest != expected_digest:
                raise RuntimeError("candidate predecessor registry digest mismatch")
            predecessor_record = json.loads(raw)
            predecessor_evidence = predecessor_record.get(
                "canonical_evidence_commit_sha_or_na"
            )
            if not isinstance(predecessor_evidence, str) or len(predecessor_evidence) != 40:
                raise RuntimeError("candidate predecessor evidence commit is not concrete")
            if not _is_strict_ancestor(predecessor_evidence, freeze_sha):
                raise RuntimeError(
                    "candidate predecessor evidence must precede successor freeze"
                )
    finally:
        after = _canonical_ref_snapshot()
        if after != before:
            raise RuntimeError("B027 candidate validation mutated canonical Git refs")


def _require_current_canonical_main() -> tuple[str, dict[str, str | None]]:
    snapshot = _canonical_ref_snapshot()
    origin_main = snapshot["refs/remotes/origin/main"]
    local_main = snapshot["refs/heads/main"]
    if origin_main is None:
        raise RuntimeError("origin/main is unavailable for canonical validation")
    if local_main is not None and local_main != origin_main:
        raise RuntimeError("local main disagrees with origin/main")
    if not _is_ancestor(CANONICAL_ENTRY_MAIN, origin_main):
        raise RuntimeError("canonical main no longer descends from the B027 entry commit")
    return origin_main, snapshot


def _validate_record_canonical(record: dict[str, Any]) -> None:
    _canonical_main, before = _require_current_canonical_main()
    try:
        validate_instance("mstr-research-experiment-v2", record, repository_root=ROOT)
    finally:
        after = _canonical_ref_snapshot()
        if after != before:
            raise RuntimeError("B027 canonical validation mutated canonical Git refs")
'''
    text = replace_once(
        text,
        old_validation,
        new_validation,
        label="validation block",
    )

    replacements = {
        "_validate_record(l0, l0_registry)": "_validate_record_candidate(l0, l0_registry)",
        "_validate_record(l1, l1_registry)": "_validate_record_candidate(l1, l1_registry)",
        "_validate_record(l0, final)": "_validate_record_candidate(l0, final)",
        "_validate_record(l1, final)": "_validate_record_candidate(l1, final)",
    }
    for old, new in replacements.items():
        text = replace_once(text, old, new, label=old)
    if "_set_local_main" in text or "_validate_record(" in text:
        raise RuntimeError("legacy canonical-ref mutation validation remains")

    text = replace_once(
        text,
        "def run() -> None:\n    script_digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()\n",
        "def run() -> None:\n"
        "    _require_trusted_canonical_entry()\n"
        "    script_digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()\n",
        label="run entry guard",
    )

    text = replace_once(
        text,
        '        "canonical_entry_main": "312d40eee8400a0dab94633f891b206f66a82855",\n'
        '        "frozen_evaluation_identity": evaluator_identity,\n',
        '        "canonical_entry_main": CANONICAL_ENTRY_MAIN,\n'
        '        "canonical_history_status": "PENDING_POST_MERGE_VALIDATION",\n'
        '        "candidate_validation_kind": "PROSPECTIVE_NO_CANONICAL_REF_REWRITE",\n'
        '        "frozen_evaluation_identity": evaluator_identity,\n',
        label="ledger status",
    )
    text = replace_once(
        text,
        '        "canonical_entry_main": "312d40eee8400a0dab94633f891b206f66a82855",\n'
        '        "harness_path": "scripts/research/b027_ladder_pilot.py",\n',
        '        "canonical_entry_main": CANONICAL_ENTRY_MAIN,\n'
        '        "canonical_history_status": "PENDING_POST_MERGE_VALIDATION",\n'
        '        "candidate_validation_kind": "PROSPECTIVE_NO_CANONICAL_REF_REWRITE",\n'
        '        "harness_path": "scripts/research/b027_ladder_pilot.py",\n',
        label="manifest status",
    )
    text = replace_once(
        text,
        '- full ledger: `artifacts/results/research/B027/campaign-ledger.json`\n',
        '- full ledger: `artifacts/results/research/B027/campaign-ledger.json`\n'
        '- premerge canonical-history status: `PENDING_POST_MERGE_VALIDATION`\n'
        '- premerge validation kind: `PROSPECTIVE_NO_CANONICAL_REF_REWRITE`\n',
        label="evidence status bullets",
    )
    evidence_para = (
        "The L1 record consumes the exact L0 promoted result through the immutable predecessor registry\n"
        "binding. Promotion policies precede their evidence commits, gate observations are derived from\n"
        "content-addressed verifier results, and the same frozen evaluator identity is used across both\n"
        "levels.\n"
    )
    text = replace_once(
        text,
        evidence_para,
        evidence_para
        + "\nPremerge candidate validation never rewrites `refs/heads/main` or\n"
        + "`refs/remotes/origin/main` and does not claim that feature-only campaign commits are\n"
        + "already canonical. Full `mstr.research-experiment.v2` canonical-history semantic\n"
        + "validation is intentionally deferred to mandatory post-merge verification on real\n"
        + "`main`, where the campaign commits must actually be canonical ancestors.\n",
        label="evidence trust note",
    )
    path.write_text(text, encoding="utf-8")


def repair_tests(root: Path) -> None:
    path = root / "tests" / "contract" / "test_b027_ladder_pilot.py"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "import hashlib\nimport json\nfrom pathlib import Path\n",
        "import hashlib\n"
        "import importlib.util\n"
        "import json\n"
        "import subprocess\n"
        "from pathlib import Path\n\n"
        "import pytest\n\n"
        "from mstr_qualify.errors import SchemaValidationError\n",
        label="test imports",
    )
    if "test_b027_canonical_validation_fails_closed_without_mutating_refs" in text:
        raise RuntimeError("regression tests already present")
    text += '''


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_b027_canonical_validation_fails_closed_without_mutating_refs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clone = tmp_path / "repo"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", str(ROOT), str(clone)],
        check=True,
        capture_output=True,
        text=True,
    )
    candidate_head = _git(ROOT, "rev-parse", "HEAD")
    canonical_entry = "312d40eee8400a0dab94633f891b206f66a82855"
    assert candidate_head != canonical_entry
    _git(clone, "checkout", "--detach", candidate_head)
    _git(clone, "update-ref", "refs/heads/main", canonical_entry)
    _git(clone, "update-ref", "refs/remotes/origin/main", canonical_entry)

    spec = importlib.util.spec_from_file_location(
        "b027_ladder_pilot_regression",
        ROOT / "scripts" / "research" / "b027_ladder_pilot.py",
    )
    assert spec is not None and spec.loader is not None
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    monkeypatch.setattr(pilot, "ROOT", clone)
    monkeypatch.setattr(
        pilot,
        "RESULT_ROOT",
        clone / "artifacts" / "results" / "research" / "B027",
    )

    record = json.loads(
        (
            clone
            / "artifacts"
            / "results"
            / "research"
            / "B027"
            / "registry"
            / "b027-l0-contract-smoke.json"
        ).read_text(encoding="utf-8")
    )
    before = {
        ref: _git(clone, "rev-parse", "--verify", f"{ref}^{{commit}}")
        for ref in ("refs/heads/main", "refs/remotes/origin/main")
    }
    with pytest.raises(SchemaValidationError):
        pilot._validate_record_canonical(record)
    after = {
        ref: _git(clone, "rev-parse", "--verify", f"{ref}^{{commit}}")
        for ref in ("refs/heads/main", "refs/remotes/origin/main")
    }
    assert after == before
    assert before == {
        "refs/heads/main": canonical_entry,
        "refs/remotes/origin/main": canonical_entry,
    }


def test_b027_harness_never_rewrites_canonical_refs() -> None:
    source = (ROOT / "scripts" / "research" / "b027_ladder_pilot.py").read_text(
        encoding="utf-8"
    )
    assert "update-ref" not in source
'''
    path.write_text(text, encoding="utf-8")


def main() -> None:
    root = Path.cwd()
    repair_script(root)
    repair_tests(root)


if __name__ == "__main__":
    main()
