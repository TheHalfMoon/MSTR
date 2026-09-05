from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()


def p(relative: str) -> Path:
    return ROOT / relative


def sha256(relative: str) -> str:
    return hashlib.sha256(p(relative).read_bytes()).hexdigest()


binding_path = p("artifacts/manifests/T031-executor-toolchain-binding.json")
binding = json.loads(binding_path.read_text(encoding="utf-8"))
dispatch = binding["dispatch_boundary"]
if not isinstance(dispatch, dict):
    raise SystemExit("dispatch boundary must be an object")
for key in (
    "manual_dispatch_branch",
    "connector_dispatch_branch_pattern",
    "connector_dispatch_event",
):
    dispatch.pop(key, None)
dispatch.update(
    {
        "canonicalization_required": True,
        "connector_dispatch_surface": "ISSUE_COMMENT_CANONICAL_MAIN",
        "connector_dispatch_issue": 167,
        "connector_dispatch_author": "TheHalfMoon",
        "connector_dispatch_author_association": "OWNER",
        "connector_dispatch_command": "T031_RUN <authorized-candidate>",
        "checkout_ref": "main",
        "max_parallel_candidates": 1,
        "max_job_minutes": 120,
    }
)

for key, relative in {
    "toolchain_lock_sha256": "artifacts/manifests/T031-executor-toolchain-lock.json",
    "toolchain_helper_sha256": "colab/mstr_executor_toolchain.py",
    "governance_script_sha256": "colab/mstr_t031_governance.py",
    "source_script_sha256": "colab/mstr_t031_source.py",
    "artifact_script_sha256": "colab/mstr_t031_artifacts.py",
    "measurement_script_sha256": "colab/mstr_t031_measure.py",
    "executor_script_sha256": "colab/mstr_t031_execute.py",
    "workflow_sha256": ".github/workflows/t031-measure.yml",
}.items():
    binding[key] = sha256(relative)

binding_path.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")


evidence_path = p("evidence/T031-executor-toolchain-binding.md")
evidence = evidence_path.read_text(encoding="utf-8")
marker = "## Dispatch lifecycle\n"
prefix, separator, _ = evidence.partition(marker)
if not separator:
    raise SystemExit("dispatch lifecycle marker missing")
replacement = """## Dispatch lifecycle

This binding PR itself performs no model access.

After this exact binding becomes canonical, connector dispatch is accepted only through the
canonical Issue #167 surface. GitHub loads `issue_comment` workflows from the default branch, so a
contributor-controlled branch cannot supply the workflow definition used for model access. The
comment must be created by repository owner `TheHalfMoon`, carry `author_association=OWNER`, and
exactly match `T031_RUN <authorized-candidate>` for one of the eight bound candidates.

The workflow verifies the event resolves to `refs/heads/main`, then explicitly checks out live
canonical `main` with persisted Git credentials disabled. Global workflow concurrency is one
candidate and `cancel-in-progress` is false. The executor rechecks live `main` immediately before
the first model-artifact byte is requested and again before reporting success. A main movement
invalidates the run.

There is no push, branch-creation, wildcard-branch, pull-request, or arbitrary-ref model-execution
trigger in the canonical T031 workflow.

Only JSON/JSONL measurement evidence is uploaded. Any identity, authority, toolchain, network,
artifact, runtime, or live-main mismatch fails closed; failed runs remain failure evidence and are
never rewritten as success.
"""
evidence_path.write_text(prefix + replacement, encoding="utf-8")


test_path = p("tests/contract/test_t031_executor_binding.py")
tests = test_path.read_text(encoding="utf-8")
if "import ast\n" not in tests:
    tests = tests.replace("import hashlib\n", "import ast\nimport hashlib\n", 1)
old_start = "def test_workflow_dispatch_is_canonical_and_branch_creation_only() -> None:\n"
if old_start not in tests:
    raise SystemExit("old dispatch test marker missing")
start = tests.index(old_start)
next_marker = "\ndef test_executor_contains_fail_closed_network_and_runtime_boundaries() -> None:\n"
end = tests.index(next_marker, start)
new_dispatch_test = '''def test_issue_comment_dispatch_is_canonical_owner_scoped_and_branch_trigger_free() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    binding = _read_json(BINDING)

    assert "issue_comment:" in workflow
    assert "workflow_dispatch:" not in workflow
    assert "\\n  push:" not in workflow
    assert "execute/t031-" not in workflow
    assert "github.event.issue.number == 167" in workflow
    assert "github.actor == 'TheHalfMoon'" in workflow
    assert "github.event.comment.user.login == 'TheHalfMoon'" in workflow
    assert "github.event.comment.author_association == 'OWNER'" in workflow
    assert '[[ "$GITHUB_EVENT_NAME" == "issue_comment" ]]' in workflow
    assert '[[ "$GITHUB_REF" == "refs/heads/main" ]]' in workflow
    assert '[[ "$ISSUE_NUMBER" == "167" ]]' in workflow
    assert "ref: main" in workflow
    assert "persist-credentials: false" in workflow
    assert "permissions:\\n  contents: read" in workflow
    assert "group: t031-governed-model-execution" in workflow
    assert "cancel-in-progress: false" in workflow
    for candidate in CANDIDATES:
        assert f"T031_RUN {candidate}" in workflow

    dispatch = binding["dispatch_boundary"]
    assert isinstance(dispatch, dict)
    assert dispatch["canonicalization_required"] is True
    assert dispatch["connector_dispatch_surface"] == "ISSUE_COMMENT_CANONICAL_MAIN"
    assert dispatch["connector_dispatch_issue"] == 167
    assert dispatch["connector_dispatch_author"] == "TheHalfMoon"
    assert dispatch["connector_dispatch_author_association"] == "OWNER"
    assert dispatch["connector_dispatch_command"] == "T031_RUN <authorized-candidate>"
    assert dispatch["checkout_ref"] == "main"
    assert dispatch["max_parallel_candidates"] == 1
    assert dispatch["max_job_minutes"] == 120

'''
tests = tests[:start] + new_dispatch_test + tests[end + 1 :]

if "def test_toolchain_subprocesses_are_bounded_and_workdir_setup_fails_closed()" not in tests:
    tests += '''\n\ndef test_toolchain_subprocesses_are_bounded_and_workdir_setup_fails_closed() -> None:
    helper = HELPER.read_text(encoding="utf-8")
    executor = EXECUTOR.read_text(encoding="utf-8")
    tree = ast.parse(helper)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_run_checked"
    ]
    assert calls
    for call in calls:
        assert any(keyword.arg == "timeout" for keyword in call.keywords)
    assert "timeout=timeout" in helper
    assert "except subprocess.TimeoutExpired as exc:" in helper
    assert executor.index("    try:\\n") < executor.index("        if workdir.exists():")
    assert executor.index("    try:\\n") < executor.index("        workdir.mkdir(parents=True)")
'''

test_path.write_text(tests, encoding="utf-8")

# Static postconditions that do not require third-party packages.
workflow = p(".github/workflows/t031-measure.yml").read_text(encoding="utf-8")
if "issue_comment:" not in workflow:
    raise SystemExit("canonical issue-comment dispatch missing")
for forbidden in ("workflow_dispatch:", "execute/t031-", "\n  push:"):
    if forbidden in workflow:
        raise SystemExit(f"forbidden dispatch surface remains: {forbidden!r}")
helper = p("colab/mstr_executor_toolchain.py").read_text(encoding="utf-8")
helper_tree = ast.parse(helper)
calls = [
    node
    for node in ast.walk(helper_tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Name)
    and node.func.id == "_run_checked"
]
if not calls or any(not any(k.arg == "timeout" for k in call.keywords) for call in calls):
    raise SystemExit("unbounded _run_checked call remains")
executor = p("colab/mstr_t031_execute.py").read_text(encoding="utf-8")
if executor.index("    try:\n") >= executor.index("        workdir.mkdir(parents=True)"):
    raise SystemExit("workdir setup is outside the fail-closed try boundary")
