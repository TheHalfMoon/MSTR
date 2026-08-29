from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path("tools/evidence/build_b028_q4_preflight_v2.py", run_name="__main__")

path = Path("tests/integration/test_cli_offline.py")
text = path.read_text(encoding="utf-8")
old = '''        "mstr-greenfield-task-v0",
        "mstr-loop-contract-v0",
        "mstr-run-event-v0",
'''
new = '''        "mstr-greenfield-task-v0",
        "mstr-loop-contract-v0",
        "mstr-q4-promotion-v0",
        "mstr-run-event-v0",
'''
if text.count(old) != 1:
    raise SystemExit("expected one offline schema-list insertion point for q4 promotion")
text = text.replace(old, new, 1)
old = '''        "mstr-task-node-v0",
        "mstr-teacher-rescue-record-v0",
        "mstr-verifier-health-v0",
'''
new = '''        "mstr-task-node-v0",
        "mstr-teacher-rescue-record-v0",
        "mstr-training-method-cell-v0",
        "mstr-verifier-health-v0",
'''
if text.count(old) != 1:
    raise SystemExit("expected one offline schema-list insertion point for training method")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
