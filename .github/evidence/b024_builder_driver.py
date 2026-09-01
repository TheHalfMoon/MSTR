from __future__ import annotations

import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: b024_builder_driver.py <builder.py>")

source_path = Path(sys.argv[1])
source = source_path.read_text(encoding="utf-8")

old_scope = '''changed = {
    line.strip()
    for line in __import__("subprocess")
    .check_output(["git", "diff", "--name-only"], text=True)
    .splitlines()
    if line.strip()
}
'''
new_scope = '''status_lines = __import__("subprocess").check_output(
    ["git", "status", "--porcelain=v1", "--untracked-files=all"], text=True
).splitlines()
changed = {line[3:] for line in status_lines if len(line) >= 4}
'''
if source.count(old_scope) != 1:
    raise RuntimeError("B024 builder scope-guard patch anchor mismatch")
source = source.replace(old_scope, new_scope)

old_classes = '''        classes = behavior.get("test_classes")
        class_set = set(classes) if isinstance(classes, list) else set()
'''
new_classes = '''        classes = behavior.get("test_classes")
        class_set = (
            {item for item in classes if isinstance(item, str)}
            if isinstance(classes, list)
            else set()
        )
'''
if source.count(old_classes) != 1:
    raise RuntimeError("B024 malformed-class hardening patch anchor mismatch")
source = source.replace(old_classes, new_classes)

old_cli_order = '''    '        "mstr-task-node-v0",\\n        "mstr-test-generation-example-v0",\\n        "mstr-teacher-rescue-record-v0",\\n',
'''
new_cli_order = '''    '        "mstr-task-node-v0",\\n        "mstr-teacher-rescue-record-v0",\\n        "mstr-test-generation-example-v0",\\n',
'''
if source.count(old_cli_order) != 1:
    raise RuntimeError("B024 CLI schema-order patch anchor mismatch")
source = source.replace(old_cli_order, new_cli_order)

exec(compile(source, str(source_path), "exec"), {"__name__": "__main__"})
