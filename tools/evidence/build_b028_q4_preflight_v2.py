from __future__ import annotations

from pathlib import Path

source_path = Path("tools/evidence/build_b028_q4_preflight.py")
source = source_path.read_text(encoding="utf-8")
old = '''replace_once(
    contracts_readme,
    "Remaining planned contracts:\\n\\n```text\\n",
    "## Frozen by B028\\n\\n```text\\n"
    "mstr.training-method-cell.v0\\n"
    "mstr.q4-promotion.v0\\n"
    "```\\n\\n"
    "B028 freezes the equivalent-method tournament cell and fail-closed Q4 checkpoint-promotion contracts. Generic framework documentation is never candidate-specific arm support evidence: every concrete finalist/method cell must bind exact backbone/framework support evidence or an exact unsupported reason before execution. A later material checkpoint may parent another material weight-changing stage only when its `mstr.q4-promotion.v0` record is `PROMOTED`. B028 itself grants no training, model-weight access, paid compute, or model-execution authority.\\n\\n"
    "Remaining planned contracts:\\n\\n```text\\n",
)
replace_once(contracts_readme, "mstr.training-method-cell.v0\\n", "",)
replace_once(contracts_readme, "mstr.q4-promotion.v0\\n", "",)
'''
new = '''replace_once(
    contracts_readme,
    "mstr.training-method-cell.v0\\nmstr.q4-promotion.v0\\nmstr.repository-health.v0\\n",
    "mstr.repository-health.v0\\n",
)
replace_once(
    contracts_readme,
    "Remaining planned contracts:\\n\\n```text\\n",
    "## Frozen by B028\\n\\n```text\\n"
    "mstr.training-method-cell.v0\\n"
    "mstr.q4-promotion.v0\\n"
    "```\\n\\n"
    "B028 freezes the equivalent-method tournament cell and fail-closed Q4 checkpoint-promotion contracts. Generic framework documentation is never candidate-specific arm support evidence: every concrete finalist/method cell must bind exact backbone/framework support evidence or an exact unsupported reason before execution. A later material checkpoint may parent another material weight-changing stage only when its `mstr.q4-promotion.v0` record is `PROMOTED`. B028 itself grants no training, model-weight access, paid compute, or model-execution authority.\\n\\n"
    "Remaining planned contracts:\\n\\n```text\\n",
)
'''
count = source.count(old)
if count != 1:
    raise SystemExit(f"expected one B028 builder ordering block; found {count}")
exec(compile(source.replace(old, new, 1), str(source_path), "exec"))
