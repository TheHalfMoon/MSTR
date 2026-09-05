from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()


def path(relative: str) -> Path:
    return ROOT / relative


workflow = '''name: T031 governed local measurement

on:
  issue_comment:
    types: [created]

permissions:
  contents: read

concurrency:
  group: t031-governed-model-execution
  cancel-in-progress: false

jobs:
  measure:
    if: ${{ github.event.issue.number == 167 && github.actor == 'TheHalfMoon' && github.event.comment.user.login == 'TheHalfMoon' && github.event.comment.author_association == 'OWNER' && startsWith(github.event.comment.body, 'T031_RUN ') }}
    runs-on: ubuntu-24.04
    timeout-minutes: 120
    env:
      PYTHONHASHSEED: "0"
      TOKENIZERS_PARALLELISM: "false"
    steps:
      - name: Resolve exact candidate and canonical dispatch boundary
        id: boundary
        shell: bash
        env:
          COMMENT_BODY: ${{ github.event.comment.body }}
          COMMENT_AUTHOR: ${{ github.event.comment.user.login }}
          COMMENT_ASSOCIATION: ${{ github.event.comment.author_association }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
        run: |
          set -euo pipefail
          [[ "$GITHUB_EVENT_NAME" == "issue_comment" ]]
          [[ "$GITHUB_REF" == "refs/heads/main" ]]
          [[ "$COMMENT_AUTHOR" == "TheHalfMoon" ]]
          [[ "$COMMENT_ASSOCIATION" == "OWNER" ]]
          [[ "$ISSUE_NUMBER" == "167" ]]
          case "$COMMENT_BODY" in
            "T031_RUN granite-4.1-3b") candidate="granite-4.1-3b" ;;
            "T031_RUN ministral-3-3b") candidate="ministral-3-3b" ;;
            "T031_RUN qwen2.5-coder-1.5b") candidate="qwen2.5-coder-1.5b" ;;
            "T031_RUN qwen3-4b") candidate="qwen3-4b" ;;
            "T031_RUN qwen3.5-2b") candidate="qwen3.5-2b" ;;
            "T031_RUN qwen3.5-4b") candidate="qwen3.5-4b" ;;
            "T031_RUN smollm3-3b") candidate="smollm3-3b" ;;
            "T031_RUN yi-coder-1.5b") candidate="yi-coder-1.5b" ;;
            *) echo "Comment is not an exact authorized T031 dispatch command" >&2; exit 1 ;;
          esac
          echo "candidate=$candidate" >> "$GITHUB_OUTPUT"

      - name: Checkout live canonical main
        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          ref: main
          fetch-depth: 1
          persist-credentials: false

      - name: Set up pinned Python
        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
        with:
          python-version: "3.11.9"
          check-latest: false

      - name: Execute governed T031 measurement
        shell: bash
        env:
          T031_CANDIDATE: ${{ steps.boundary.outputs.candidate }}
        run: |
          set -euo pipefail
          mkdir -p "$RUNNER_TEMP/t031-out"
          python colab/mstr_t031_execute.py \
            --candidate "$T031_CANDIDATE" \
            --output-dir "$RUNNER_TEMP/t031-out" \
            --workdir "$RUNNER_TEMP/t031-work"

      - name: Upload durable JSON evidence only
        if: ${{ always() }}
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: t031-${{ steps.boundary.outputs.candidate }}
          path: |
            ${{ runner.temp }}/t031-out/*.json
            ${{ runner.temp }}/t031-out/*.jsonl
          if-no-files-found: error
          retention-days: 14
'''
path(".github/workflows/t031-measure.yml").write_text(workflow, encoding="utf-8")

helper_path = path("colab/mstr_executor_toolchain.py")
helper = helper_path.read_text(encoding="utf-8")
old_run = '''def _run_checked(argv: list[str], *, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
    )
    if completed.returncode != 0:
        diagnostic = (completed.stdout + "\\n" + completed.stderr).strip()[-4000:]
        raise ToolchainError(f"command failed ({completed.returncode}): {argv!r}\\n{diagnostic}")
    return completed.stdout.strip()
'''
new_run = '''def _run_checked(
    argv: list[str], *, timeout_seconds: float, env: dict[str, str] | None = None
) -> str:
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            env=env,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolchainError(
            f"command timed out after {timeout_seconds} seconds: {argv!r}"
        ) from exc
    if completed.returncode != 0:
        diagnostic = (completed.stdout + "\\n" + completed.stderr).strip()[-4000:]
        raise ToolchainError(f"command failed ({completed.returncode}): {argv!r}\\n{diagnostic}")
    return completed.stdout.strip()
'''
if old_run not in helper:
    raise SystemExit("_run_checked patch anchor missing")
helper = helper.replace(old_run, new_run, 1)

replacements = [
    ("output = _run_checked(argv)", "output = _run_checked(argv, timeout_seconds=30)"),
    (
        '_run_checked([sys.executable, "-m", "venv", str(venv)])',
        '_run_checked([sys.executable, "-m", "venv", str(venv)], timeout_seconds=120)',
    ),
    (
        '''            str(pip_wheel),
        ]
    )
    package_wheels''',
        '''            str(pip_wheel),
        ],
        timeout_seconds=300,
    )
    package_wheels''',
    ),
    (
        '''            *package_wheels,
        ]
    )
    shutil.rmtree''',
        '''            *package_wheels,
        ],
        timeout_seconds=300,
    )
    shutil.rmtree''',
    ),
    (
        '_run_checked(["git", "-C", str(destination), "init"], env=env)',
        '_run_checked(["git", "-C", str(destination), "init"], timeout_seconds=60, env=env)',
    ),
    (
        '_run_checked(["git", "-C", str(destination), "remote", "add", "origin", repository], env=env)',
        '''_run_checked(
        ["git", "-C", str(destination), "remote", "add", "origin", repository],
        timeout_seconds=60,
        env=env,
    )''',
    ),
    (
        '''        ["git", "-C", str(destination), "fetch", "--depth", "1", "origin", commit],
        env=env,
    )''',
        '''        ["git", "-C", str(destination), "fetch", "--depth", "1", "origin", commit],
        timeout_seconds=300,
        env=env,
    )''',
    ),
    (
        '_run_checked(["git", "-C", str(destination), "checkout", "--detach", commit], env=env)',
        '''_run_checked(
        ["git", "-C", str(destination), "checkout", "--detach", commit],
        timeout_seconds=60,
        env=env,
    )''',
    ),
    (
        'actual = _run_checked(["git", "-C", str(destination), "rev-parse", "HEAD"], env=env)',
        '''actual = _run_checked(
        ["git", "-C", str(destination), "rev-parse", "HEAD"],
        timeout_seconds=60,
        env=env,
    )''',
    ),
    (
        '_run_checked(["cmake", "-S", str(destination), "-B", str(build_dir), *build_flags], env=env)',
        '''_run_checked(
        ["cmake", "-S", str(destination), "-B", str(build_dir), *build_flags],
        timeout_seconds=300,
        env=env,
    )''',
    ),
    (
        '''        ],
        env=env,
    )
    executable = build_dir''',
        '''        ],
        timeout_seconds=900,
        env=env,
    )
    executable = build_dir''',
    ),
]
for old, new in replacements:
    if old not in helper:
        raise SystemExit(f"helper patch anchor missing: {old[:80]!r}")
    helper = helper.replace(old, new, 1)
helper_path.write_text(helper, encoding="utf-8")

executor_path = path("colab/mstr_t031_execute.py")
executor = executor_path.read_text(encoding="utf-8")
old_executor = '''    workdir = args.workdir.resolve()
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    head = "UNKNOWN"
    try:
        head = _require_live_main(repo_root)
'''
new_executor = '''    workdir = args.workdir.resolve()

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    head = "UNKNOWN"
    try:
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True)
        head = _require_live_main(repo_root)
'''
if old_executor not in executor:
    raise SystemExit("executor patch anchor missing")
executor_path.write_text(executor.replace(old_executor, new_executor, 1), encoding="utf-8")

evidence_path = path("evidence/T031-executor-toolchain-binding.md")
evidence = evidence_path.read_text(encoding="utf-8")
start = evidence.index("## Dispatch lifecycle\n")
evidence_tail = '''## Dispatch lifecycle

This binding PR itself performs no model access.

After this exact binding becomes canonical, connector dispatch uses an `issue_comment` event that
GitHub loads from the default branch. The only accepted surface is canonical Issue #167, the
existing Founder-decision surface. The comment must be created by repository owner `TheHalfMoon`,
carry `author_association=OWNER`, and exactly match `T031_RUN <authorized-candidate>` for one of the
eight bound candidates. All other comments are ignored before runner allocation or fail closed
before model access.

This removes branch-triggered execution entirely: no contributor-controlled branch can supply the
workflow definition used for T031 model access. The job explicitly checks that the event resolves to
`refs/heads/main`, then checks out live canonical `main` with persisted Git credentials disabled.

Global workflow concurrency is one candidate and `cancel-in-progress` is false. The executor
rechecks live `main` again immediately before model access and again before reporting success. A
main movement invalidates the run.

Only JSON/JSONL measurement evidence is uploaded. Any identity, authority, toolchain, network,
artifact, runtime, or live-main mismatch fails closed; failed runs remain failure evidence and are
never rewritten as success.
'''
evidence_path.write_text(evidence[:start] + evidence_tail, encoding="utf-8")

test_path = path("tests/contract/test_t031_executor_binding.py")
test = test_path.read_text(encoding="utf-8")
test = test.replace("import hashlib\n", "import ast\nimport hashlib\n", 1)
start = test.index("def test_workflow_dispatch_is_canonical_and_branch_creation_only()")
end = test.index("\ndef test_executor_contains_fail_closed_network_and_runtime_boundaries()", start)
new_test = '''def test_issue_comment_dispatch_is_canonical_owner_scoped_and_branch_trigger_free() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    binding = _read_json(BINDING)

    assert "issue_comment:" in workflow
    assert "workflow_dispatch:" not in workflow
    assert '\"execute/t031-*\"' not in workflow
    assert "\\n  push:" not in workflow
    assert "github.event.issue.number == 167" in workflow
    assert "github.actor == 'TheHalfMoon'" in workflow
    assert "github.event.comment.user.login == 'TheHalfMoon'" in workflow
    assert "github.event.comment.author_association == 'OWNER'" in workflow
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


def test_toolchain_subprocesses_are_bounded_and_workdir_setup_fails_closed() -> None:
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
        assert any(keyword.arg == "timeout_seconds" for keyword in call.keywords)
    assert "timeout=timeout_seconds" in helper
    assert "except subprocess.TimeoutExpired as exc:" in helper
    assert executor.index("    try:\\n") < executor.index("        if workdir.exists():")
    assert executor.index("    try:\\n") < executor.index("        workdir.mkdir(parents=True)")

'''
test = test[:start] + new_test + test[end + 1 :]
test_path.write_text(test, encoding="utf-8")

binding_path = path("artifacts/manifests/T031-executor-toolchain-binding.json")
binding = json.loads(binding_path.read_text(encoding="utf-8"))
dispatch = binding["dispatch_boundary"]
for key in ("manual_dispatch_branch", "connector_dispatch_branch_pattern", "connector_dispatch_event"):
    dispatch.pop(key, None)
dispatch.update(
    {
        "connector_dispatch_surface": "ISSUE_COMMENT_CANONICAL_MAIN",
        "connector_dispatch_issue": 167,
        "connector_dispatch_author": "TheHalfMoon",
        "connector_dispatch_author_association": "OWNER",
        "connector_dispatch_command": "T031_RUN <authorized-candidate>",
    }
)

# Validate every helper command is statically bounded before hash refresh.
helper_tree = ast.parse(helper_path.read_text(encoding="utf-8"))
calls = [
    node
    for node in ast.walk(helper_tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Name)
    and node.func.id == "_run_checked"
]
if not calls or any(not any(k.arg == "timeout_seconds" for k in call.keywords) for call in calls):
    raise SystemExit("unbounded _run_checked call remains")


def sha(relative: str) -> str:
    return hashlib.sha256(path(relative).read_bytes()).hexdigest()


binding["toolchain_helper_sha256"] = sha("colab/mstr_executor_toolchain.py")
binding["executor_script_sha256"] = sha("colab/mstr_t031_execute.py")
binding["workflow_sha256"] = sha(".github/workflows/t031-measure.yml")
binding_path.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
