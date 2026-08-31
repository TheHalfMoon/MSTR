from __future__ import annotations

import subprocess
from pathlib import Path

SOURCE = Path("/tmp/a011-source.yml")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label} marker mismatch")
    return text.replace(old, new, 1)


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    marker = "          python - <<'PY'\n"
    start = text.index(marker, text.index("- name: Materialize A011 contract package")) + len(marker)
    end = text.index("          PY\n", start)
    lines = []
    for line in text[start:end].splitlines():
        lines.append(line[10:] if line.startswith("          ") else line)
    materializer = "\n".join(lines) + "\n"
    old_scope = '''paths = {line[3:] for line in subprocess.check_output(["git", "status", "--short"], text=True).splitlines()}\nif paths != expected:\n    raise SystemExit(f"unexpected A011 scope: {sorted(paths)}")'''
    new_scope = '''tracked = set(subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines())\nuntracked = set(subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], text=True).splitlines())\npaths = tracked | untracked\nif paths != expected:\n    raise SystemExit(f"unexpected A011 initial scope: {sorted(paths)}")'''
    materializer = replace_once(materializer, old_scope, new_scope, "initial scope")
    exec(compile(materializer, "/tmp/a011-materializer.py", "exec"), {"__name__": "__main__"})

    path = Path("tests/contract/test_schemas.py")
    schema_text = path.read_text(encoding="utf-8")
    schema_marker = '    "mstr-capability-profile-v0": (\n'
    schema_block = '''    "mstr-environment-manifest-v0": (\n        ROOT\n        / "specs"\n        / "001-agent-harness-verified-loop-foundation"\n        / "contracts"\n        / "mstr-environment-manifest-v0.schema.json"\n    ),\n    "mstr-setup-manifest-v0": (\n        ROOT\n        / "specs"\n        / "001-agent-harness-verified-loop-foundation"\n        / "contracts"\n        / "mstr-setup-manifest-v0.schema.json"\n    ),\n    "mstr-verifier-manifest-v0": (\n        ROOT\n        / "specs"\n        / "001-agent-harness-verified-loop-foundation"\n        / "contracts"\n        / "mstr-verifier-manifest-v0.schema.json"\n    ),\n'''
    path.write_text(
        replace_once(schema_text, schema_marker, schema_block + schema_marker, "design schema override"),
        encoding="utf-8",
    )

    path = Path("tests/integration/test_cli_offline.py")
    cli_text = path.read_text(encoding="utf-8")
    for old, new in (
        (
            '        "mstr-difficulty-calibration-v0",\n',
            '        "mstr-difficulty-calibration-v0",\n        "mstr-environment-manifest-v0",\n',
        ),
        (
            '        "mstr-self-alignment-generation-v0",\n',
            '        "mstr-self-alignment-generation-v0",\n        "mstr-setup-manifest-v0",\n',
        ),
        (
            '        "mstr-verifier-health-v0",\n',
            '        "mstr-verifier-health-v0",\n        "mstr-verifier-manifest-v0",\n',
        ),
    ):
        cli_text = replace_once(cli_text, old, new, "CLI schema expectation")
    path.write_text(cli_text, encoding="utf-8")

    path = Path("tests/contract/test_environment_verifier_contracts.py")
    contract_text = path.read_text(encoding="utf-8")
    old_fixture = '''def _fixture(kind: str, name: str) -> dict[str, object]:\n    return json.loads((ROOT / "tests" / "fixtures" / "schemas" / kind / f"{name}.json").read_text(encoding="utf-8"))\n'''
    new_fixture = '''def _fixture(kind: str, name: str) -> dict[str, object]:\n    path = ROOT / "tests" / "fixtures" / "schemas" / kind / f"{name}.json"\n    return json.loads(path.read_text(encoding="utf-8"))\n'''
    old_design = '''    design = ROOT / "specs" / "001-agent-harness-verified-loop-foundation" / "contracts" / f"{name}.schema.json"\n'''
    new_design = '''    design = (\n        ROOT\n        / "specs"\n        / "001-agent-harness-verified-loop-foundation"\n        / "contracts"\n        / f"{name}.schema.json"\n    )\n'''
    contract_text = replace_once(contract_text, old_fixture, new_fixture, "fixture formatting")
    contract_text = replace_once(contract_text, old_design, new_design, "design path formatting")
    path.write_text(contract_text, encoding="utf-8")

    expected = {
        "evidence/mstr-000a/A011-env-verifier-contracts.md",
        "schemas/mstr-environment-manifest-v0.schema.json",
        "schemas/mstr-setup-manifest-v0.schema.json",
        "schemas/mstr-verifier-manifest-v0.schema.json",
        "specs/001-agent-harness-verified-loop-foundation/contracts/mstr-environment-manifest-v0.schema.json",
        "specs/001-agent-harness-verified-loop-foundation/contracts/mstr-setup-manifest-v0.schema.json",
        "specs/001-agent-harness-verified-loop-foundation/contracts/mstr-verifier-manifest-v0.schema.json",
        "src/mstr_qualify/schemas.py",
        "tests/contract/test_environment_verifier_contracts.py",
        "tests/contract/test_schemas.py",
        "tests/fixtures/schemas/invalid/mstr-environment-manifest-v0.json",
        "tests/fixtures/schemas/invalid/mstr-setup-manifest-v0.json",
        "tests/fixtures/schemas/invalid/mstr-verifier-manifest-v0.json",
        "tests/fixtures/schemas/valid/mstr-environment-manifest-v0.json",
        "tests/fixtures/schemas/valid/mstr-setup-manifest-v0.json",
        "tests/fixtures/schemas/valid/mstr-verifier-manifest-v0.json",
        "tests/integration/test_cli_offline.py",
    }
    tracked = set(subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines())
    untracked = set(
        subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], text=True).splitlines()
    )
    actual = tracked | untracked
    if actual != expected:
        raise SystemExit(f"unexpected A011 final scope: {sorted(actual)}")
    print("A011_FINAL_SCOPE_START")
    print("\n".join(sorted(actual)))
    print("A011_FINAL_SCOPE_END")


if __name__ == "__main__":
    main()
