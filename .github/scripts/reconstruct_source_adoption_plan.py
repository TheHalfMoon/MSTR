from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path('.')
BASE = '5e74e77c1fc86d4ebc7e64654f45bd18f565edd6'
BASE_TREE = '66120bf247e7d9b9da34d5d47603493c8dce4c30'

REVISIONS = {
    'c389f96a06005300336904239c409258129812c9': 'c389f96bf3a9b6807cb71ed6bdad5849be0df6d8',
    'd8563a7d213dd2472c18314992b9435527a11eaf': '04d809ceab9df28f9adaed044884180159172930',
    'a978f8924522bb72c0d5a876b3990d41d432decf': '5c995c365dfb1fd5bc56fda688be5d8538f9931f',
    '2a8d8b739a7be305f570963240f8f96ba62c90d0': '5dc9490bb35f9729ef2c95d00a19ccd30c26339c',
    'dbae8d5667c61f5f4b313b0169d8acd8f102373a': '1891e22b25bda4a4e88e23b3866c3ee7a127e3be',
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    if not text.endswith('\n'):
        text += '\n'
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if text.count(old) != 1:
        raise RuntimeError(f'expected one anchor in {path}: {old!r}')
    write(path, text.replace(old, new, 1))


research = 'specs/002-code-model-supremacy-foundation/research-source-adoption-2026-09-08.md'
text = read(research)
for old, new in REVISIONS.items():
    if old not in text:
        raise RuntimeError(f'missing research revision {old}')
    text = text.replace(old, new)
text = text.replace('Status: PLANNING_RESEARCH_CANDIDATE', 'Status: CANONICAL_RESEARCH_INPUT_ON_MERGE')
text += f'''\n## Revision re-verification on canonical planning base\n\nPlanning base: `{BASE}`  \nPlanning-base tree: `{BASE_TREE}`  \nReverified: 2026-09-08\n\nAll 18 upstream refs were re-read before reconstruction. Thirteen remained unchanged. Five moved and are repinned here: `deepseek-ai/deepseek-harness`, `SWE-agent/mini-swe-agent`, `SWE-agent/SWE-ReX`, `Aider-AI/aider`, and `ifm-ai/xllm`. Revision movement alone does not change a disposition. Any future copied/adapted primitive must independently reverify and bind its exact adopted revision in a `SourceAdoptionRecord`.\n'''
write(research, text)

snapshot_path = 'artifacts/manifests/MSTR-source-adoption-research-snapshot-2026-09-08.json'
snapshot = json.loads(read(snapshot_path))
snapshot['canonical_planning_base'] = BASE
snapshot['canonical_planning_base_tree'] = BASE_TREE
snapshot['revision_reverification'] = {
    'reverified_date': '2026-09-08',
    'source_count': 18,
    'unchanged_source_count': 13,
    'changed_source_count': 5,
    'changed_sources': ['deepseek-harness', 'mini-swe-agent', 'swe-rex', 'aider', 'ifm-xllm'],
}
revision_by_id = {
    'deepseek-harness': REVISIONS['c389f96a06005300336904239c409258129812c9'],
    'mini-swe-agent': REVISIONS['d8563a7d213dd2472c18314992b9435527a11eaf'],
    'swe-rex': REVISIONS['a978f8924522bb72c0d5a876b3990d41d432decf'],
    'aider': REVISIONS['2a8d8b739a7be305f570963240f8f96ba62c90d0'],
    'ifm-xllm': REVISIONS['dbae8d5667c61f5f4b313b0169d8acd8f102373a'],
}
for item in snapshot['sources']:
    if item['source_id'] in revision_by_id:
        item['observed_revision'] = revision_by_id[item['source_id']]
write(snapshot_path, json.dumps(snapshot, indent=2) + '\n')

strategy = 'docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md'
replace_once(strategy, 'Status: PLANNED_CANONICAL_AMENDMENT_CANDIDATE', 'Status: CANONICAL_PLANNING_AMENDMENT_ON_MERGE')
with (ROOT / strategy).open('a', encoding='utf-8') as fh:
    fh.write(f'''\n## 18. Canonical planning-base reconstruction\n\nThis amendment was reconstructed from exact canonical `main` `{BASE}` rather than rebasing or merging the stale planning branch. The prior research artifacts were treated as source material, all 18 upstream refs were reverified, and the five moved heads were repinned in the companion snapshot.\n\nCompleted B014-B030 history remains closed and unchanged. B031 retains its existing exact prerequisites and authority semantics. B032 is the first remaining task that may freeze these interfaces into downstream entry contracts; B033 independently red-teams them; B034 may close only after these obligations and all earlier canonical requirements are satisfied.\n\nThis planning amendment creates no model access, model execution, dataset admission, training, paid compute, external dispatch, or production-release authority.\n''')

tasks_path = 'specs/002-code-model-supremacy-foundation/tasks.md'
tasks = read(tasks_path)
b031_match = re.search(r'- \[ \] \*\*B031 .*?(?=\n- \[ \] \*\*B032 )', tasks, flags=re.S)
if not b031_match:
    raise RuntimeError('B031 block missing')
b031_before = b031_match.group(0)

b032 = '''- [ ] **B032 Amend MSTR-001/MSTR-002/MSTR-003 entry requirements and downstream acceleration obligations.**
  Prerequisite: B031 `COMPLETE_CANONICAL`. Consume `docs/canonical/MSTR_FRONTIER_ACCELERATION_STRATEGY.md`, `docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md`, the canonical B013 frontier snapshot, and the source-adoption research snapshot. Preserve all existing checkpoint-lineage, executable-RL, targeted-feedback, low-bit/runtime, adaptive-effort, Q4-promotion, and sealed-evaluation obligations. In addition, freeze the downstream source-adoption interfaces `SourceAdoptionRecord`, `ExecutionBackendProfile`, `ResumableTaskCheckpoint`, `ImprovementDecisionRecord`, `RepositoryContextIndexProfile`, and `TrainingBackendParityRecord`; require `MINIMAL_BASH_LINEAR_BASELINE` as the anti-complexity control; require baseline-first runtime acceleration; require immutable upstream revision/update/rollback governance; and carry behavioral-reconstruction evaluation into the appropriate downstream evaluation plan. Source-code permission MUST remain distinct from data admission, model-weight authority, training authority, and external-effect authority. B032 itself authorizes none of those external effects.
  Outputs: roadmap/training strategy/preplan amendments, `evidence/mstr-000b/B032-downstream-contracts.md`.
'''

b033 = '''- [ ] **B033 Independent consistency/red-team review.**  
  Prerequisite: B032 `COMPLETE_CANONICAL`. Review all existing frontier/candidate/fairness/leakage/rights/reward-hacking/task-gate/teacher/tokenizer/Q4/low-bit/hardware/runtime/attribution/WePLD/8GB obligations. Additionally red-team source-adoption provenance, license/NOTICE retention, transitive dependencies/assets, source-code-permission conflation with data/model/training authority, mutable-upstream dependencies, dependency bloat, stale repository-context indexes, checkpoint secret leakage, optimizer/evaluator separation, execution-backend isolation/fallback semantics, training-backend semantic divergence, donor benchmark/speed claim laundering, and rollback failure. Confirm completed B014-B030 history was not reopened and B031 prerequisites were not weakened. Resolve all material findings.
  Outputs: `evidence/mstr-000b/B033-independent-review.md`.
'''

tasks, n1 = re.subn(r'- \[ \] \*\*B032 .*?(?=\n- \[ \] \*\*B033 )', b032.rstrip(), tasks, count=1, flags=re.S)
tasks, n2 = re.subn(r'- \[ \] \*\*B033 .*?(?=\n- \[ \] \*\*B034 )', b033.rstrip(), tasks, count=1, flags=re.S)
if (n1, n2) != (1, 1):
    raise RuntimeError(f'B032/B033 replacement failure: {(n1, n2)}')
write(tasks_path, tasks)

if b031_before not in read(tasks_path):
    raise RuntimeError('B031 block changed unexpectedly')

contract = '''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "artifacts/manifests/MSTR-source-adoption-research-snapshot-2026-09-08.json"
TASKS = ROOT / "specs/002-code-model-supremacy-foundation/tasks.md"
CATALOG = ROOT / "configs/task-gate/mstr-000b.json"
STRATEGY = ROOT / "docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md"


def test_source_adoption_amendment_is_planning_only() -> None:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert len(snapshot["sources"]) == 18
    boundary = snapshot["authority_boundary"]
    assert boundary["source_code_permission_is_data_admission"] is False
    assert boundary["source_code_permission_is_model_weight_authority"] is False
    assert boundary["source_code_permission_is_training_authority"] is False
    assert boundary["source_code_permission_is_external_effect_authority"] is False
    assert boundary["training"] is False
    assert boundary["paid_cost_usd"] == 0.0


def test_completed_history_and_b031_machine_gate_are_unchanged() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["tasks"]
    for task_id in [f"B{i:03d}" for i in range(14, 31)]:
        assert catalog[task_id]["canonical_state"] == "COMPLETE_CANONICAL"
    assert catalog["B031"]["canonical_state"] == "PENDING"
    assert catalog["B032"]["prerequisites"] == ["B031"]
    assert catalog["B033"]["prerequisites"] == ["B032"]


def test_b032_b033_bind_source_adoption_without_authority_expansion() -> None:
    tasks = TASKS.read_text(encoding="utf-8")
    strategy = STRATEGY.read_text(encoding="utf-8")
    for token in (
        "SourceAdoptionRecord",
        "ExecutionBackendProfile",
        "ResumableTaskCheckpoint",
        "ImprovementDecisionRecord",
        "RepositoryContextIndexProfile",
        "TrainingBackendParityRecord",
        "MINIMAL_BASH_LINEAR_BASELINE",
    ):
        assert token in tasks
        assert token in strategy
    assert "B032 itself authorizes none of those external effects" in tasks
    assert "source-code-permission conflation" in tasks
'''
write('tests/contract/test_source_adoption_plan.py', contract)
