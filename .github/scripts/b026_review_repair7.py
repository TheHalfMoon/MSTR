from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path("src/mstr_qualify/schemas.py")
TESTS = Path("tests/contract/test_research_ladder_contract.py")
CONFIG = Path("configs/research/mstr-research-ladder-v0.json")
EVIDENCE = Path("evidence/mstr-000b/B026-research-ladder.md")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one repair anchor in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


source_anchor = '''                        if nested_errors:\n                            errors.append(\n                                "$.predecessor_promotion: referenced predecessor record is invalid"\n                            )\n                        if predecessor_record.get("experiment_id") != predecessor_id:\n'''
source_replacement = '''                        if nested_errors:\n                            errors.append(\n                                "$.predecessor_promotion: referenced predecessor record is invalid"\n                            )\n                        predecessor_evidence_sha = predecessor_record.get(\n                            "canonical_evidence_commit_sha_or_na"\n                        )\n                        if not _b026_strictly_precedes(\n                            repository_root,\n                            predecessor_evidence_sha,\n                            freeze_commit_sha,\n                        ):\n                            errors.append(\n                                "$.predecessor_promotion: predecessor canonical evidence must "\n                                "strictly precede current campaign freeze"\n                            )\n                        if predecessor_record.get("experiment_id") != predecessor_id:\n'''
replace_once(SOURCE, source_anchor, source_replacement)

config = json.loads(CONFIG.read_text(encoding="utf-8"))
if not isinstance(config, dict):
    raise SystemExit("B026 ladder config must be an object")
promotion_policy = config.get("promotion_policy")
if not isinstance(promotion_policy, dict):
    raise SystemExit("B026 promotion_policy must be an object")
if "predecessor_evidence_must_precede_current_policy_freeze" in promotion_policy:
    raise SystemExit("causal predecessor policy marker already exists")
promotion_policy["predecessor_evidence_must_precede_current_policy_freeze"] = True
CONFIG.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

test_anchor = '''def test_research_experiment_enforces_material_count_and_declared_budgets() -> None:\n'''
test_insert = '''def test_predecessor_evidence_must_precede_current_policy_freeze_on_merge_history(\n    tmp_path: Path,\n) -> None:\n    task_id = "B027"\n    campaign_id = "predecessor-causality-fixture"\n    l0 = _make_level_record(0, task_id=task_id, campaign_id=campaign_id)\n    _prepare_policy_and_gate_evidence(tmp_path, l0)\n    l0_freeze = str(l0["campaign_freeze_commit_sha_or_na"])\n    l0_evidence = str(l0["canonical_evidence_commit_sha_or_na"])\n    _git(tmp_path, "branch", "predecessor-evidence", l0_evidence)\n\n    _git(tmp_path, "checkout", "-b", "current-policy", l0_freeze)\n    l0_sha = _write_json_with_sha(\n        _registry_path(tmp_path, task_id, str(l0["experiment_id"])),\n        l0,\n    )\n    l1 = _make_level_record(\n        1,\n        task_id=task_id,\n        campaign_id=campaign_id,\n        predecessor_id=str(l0["experiment_id"]),\n        predecessor_sha=l0_sha,\n        predecessor_result=str(l0["promoted_result_id_or_na"]),\n    )\n    _prepare_policy_and_gate_evidence(tmp_path, l1)\n    l1_freeze = str(l1["campaign_freeze_commit_sha_or_na"])\n\n    ancestry = subprocess.run(\n        ["git", "merge-base", "--is-ancestor", l0_evidence, l1_freeze],\n        cwd=tmp_path,\n        check=False,\n        capture_output=True,\n        text=True,\n    )\n    assert ancestry.returncode == 1\n\n    _git(\n        tmp_path,\n        "merge",\n        "--no-ff",\n        "predecessor-evidence",\n        "-m",\n        "merge predecessor evidence after current policy freeze",\n    )\n    canonical_main = _git(tmp_path, "rev-parse", "HEAD")\n    _git(tmp_path, "branch", "-f", "main", canonical_main)\n\n    with pytest.raises(\n        ValueError,\n        match="predecessor canonical evidence must strictly precede current campaign freeze",\n    ):\n        validate_instance("mstr-research-experiment-v2", l1, repository_root=tmp_path)\n\n\n'''
replace_once(TESTS, test_anchor, test_insert + test_anchor)

evidence = EVIDENCE.read_text(encoding="utf-8")
marker = "## Fresh exact-head CodeRabbit review finding on `f0cee46975693b52fc5f7e38677116b94ca98420`"
if marker in evidence:
    raise SystemExit("repair7 evidence section already exists")
append = f'''\n\n{marker}\n\nFresh independent CodeRabbit issue review comment `5515461479` reviewed exact head `f0cee46975693b52fc5f7e38677116b94ca98420` against canonical base `823cd7ec3b4c537876a0795d0f0f8d4bd75acd85` and resolved tree `6537e40ac335a4598a82b082e2e863332de9f31d`. It found one High causal-ordering defect: a higher-level policy freeze could reference a predecessor registry record whose own canonical evidence commit was only on a sibling or later-merged canonical history path, so the predecessor `PROMOTE` outcome was not necessarily available when the higher-level policy froze.\n\nThis bounded repair makes predecessor evidence causality machine-enforced. For L1-L4 campaign records, the resolved predecessor's `canonical_evidence_commit_sha_or_na` must be a strict canonical-main ancestor of the current `campaign_freeze_commit_sha_or_na`. The ladder promotion policy records this antecedence rule explicitly. An adversarial merge-history test constructs a predecessor evidence commit on a sibling history path, makes the predecessor registry record visible at the current policy freeze, later merges both paths into canonical main, and proves validation rejects the causally unavailable predecessor outcome. The existing linear promoted-chain tests continue to prove valid sequential promotion.\n\nNo task ledger, task-gate state, or authority artifact is changed. This repair grants no model execution, network model/teacher calls, paid compute/API, model-weight access, dataset ingestion, verifier execution, training/RL, research-campaign execution, Q4 execution, or production-release authority. The finding is not considered resolved by prose or a local patch; guarded publication, fresh exact-head qualification, fresh independent substantive review, zero unresolved actionable findings, and mandatory premerge verification remain required.\n'''
EVIDENCE.write_text(evidence.rstrip() + append + "\n", encoding="utf-8")
