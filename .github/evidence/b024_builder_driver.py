from __future__ import annotations

import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: b024_builder_driver.py <builder.py>")

source_path = Path(sys.argv[1])
source = source_path.read_text(encoding="utf-8")
old = '''changed = {
    line.strip()
    for line in __import__("subprocess")
    .check_output(["git", "diff", "--name-only"], text=True)
    .splitlines()
    if line.strip()
}
'''
new = '''status_lines = __import__("subprocess").check_output(
    ["git", "status", "--porcelain=v1", "--untracked-files=all"], text=True
).splitlines()
changed = {line[3:] for line in status_lines if len(line) >= 4}
'''
if source.count(old) != 1:
    raise RuntimeError("B024 builder scope-guard patch anchor mismatch")
source = source.replace(old, new)
exec(compile(source, str(source_path), "exec"), {"__name__": "__main__"})
