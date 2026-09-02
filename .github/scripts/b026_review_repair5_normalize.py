from pathlib import Path

for relative in (
    "evidence/mstr-000b/B026-research-ladder.md",
    "tests/contract/test_research_ladder_contract.py",
):
    path = Path(relative)
    path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")
