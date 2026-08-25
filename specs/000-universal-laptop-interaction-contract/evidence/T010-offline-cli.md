# T010 — Dependency-Light Offline CLI Commands

**Task:** MSTR-000 / T010  
**Canonical base:** `e042b3397af30156a243dc8a981f4f2bda6fa438`  
**Branch:** `task/000-t010-offline-cli`  
**Scope:** offline CLI command families `validate`, `rights`, `candidate static`, `manifest validate` only. No model weights, no candidate execution, no benchmark execution, no paid API, no rented compute, no network service access, and no training.

## Implemented commands

```text
mstr-qualify validate [paths...]
mstr-qualify rights <candidate-config>
mstr-qualify candidate static <candidate-config>
mstr-qualify manifest validate <manifest> [--kind {candidate,task,benchmark}]
```

`validate` with no arguments self-checks every registered repository-local schema (`Draft202012Validator.check_schema` through T004) and verifies that each canonical valid fixture passes and each canonical invalid fixture is rejected. With explicit paths, it validates each JSON file against its auto-detected contract: candidate/task/benchmark manifests route through the T008 loaders; run-evidence and interaction-contract records validate against their registered schemas.

`rights` loads a candidate config through the strict schema loader and then recomputes primary eligibility through the T006 fail-closed evaluator. A permissive-looking declared `decision` cannot bypass recomputation from evidence facts.

`candidate static` reports a static qualification summary bound to the exact source-file SHA-256 plus a stable record ID over that hash. Schema validity comes from the loader; rights are recomputed, not trusted. The command never mutates records, writes artifacts, or changes admission state — that authority remains with later canonical tasks (T012+). It never downloads weights or accesses any network resource.

`manifest validate` validates task/candidate/benchmark manifests locally through T008 loaders, with schema-version auto-detection and an explicit `--kind` override for files whose version cannot identify a kind.

## Exit-code contract

```text
0 = requested check/decision passed
1 = requested check/decision ran and failed (schema-invalid input, rights-ineligible candidate, invalid manifest)
2 = invocation/configuration/environment error (missing file, unknown command, undetectable manifest kind)
```

All stdout output is deterministic JSON (`sort_keys=True, indent=2`). Errors that are invocation/environment failures print structured JSON to stderr with a stable code.

## Offline discipline

Every command performs local filesystem reads only. The integration suite blocks `socket.socket` creation for the duration of every test, so any attempted outbound connection fails the test loudly. No command accepts gated terms, contacts a provider, executes a model, or fetches remote resources.

## Exact prepared-source validation

```text
Python = 3.14.0 (.venv via uv)
pytest = 9.1.1 / full suite = 168 passed (146 pre-existing + 22 new)
ruff (new files cli.py + tests/integration/test_cli_offline.py) = All checks passed
mypy --strict (src/mstr_qualify/cli.py standalone) = Success, no issues
```

Pre-existing E501 violations in earlier-task files remain untouched; T009 evidence defers repository-wide ruff/mypy closeout to T011. The stale T003 bootstrap expectation (`main(["validate"])` must fail closed) was updated because T010 now implements exactly that command family; an unimplemented family (`measure`) still fails closed with exit 2.

No GitHub Actions/CI PASS is claimed unless an exact-head run appears.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
BENCHMARK_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```

## Result candidate

```text
T010_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T011
```
