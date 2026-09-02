from __future__ import annotations

from pathlib import Path

SCHEMAS = Path("src/mstr_qualify/schemas.py")
TESTS = Path("tests/contract/test_research_ladder_contract.py")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one replacement for {old!r}, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def split_error_literal(text: str, prefix: str, suffix: str) -> str:
    return f'                                "{prefix}"\n                                "{suffix}"'


def harden_schemas() -> None:
    replacements = {
        '                                "$.predecessor_promotion.experiment_id: registry record identity mismatch"': split_error_literal(
            "$.predecessor_promotion.experiment_id: registry record ", "identity mismatch"
        ),
        '                                "$.predecessor_promotion: registry record must be immediate predecessor level"': split_error_literal(
            "$.predecessor_promotion: registry record must be immediate ", "predecessor level"
        ),
        '                                "$.predecessor_promotion: registry predecessor must have PROMOTE decision"': split_error_literal(
            "$.predecessor_promotion: registry predecessor must have ", "PROMOTE decision"
        ),
        '                    "$.q4_promotion_record_identity_or_na: L4 PROMOTE requires concrete Q4 promotion evidence"': (
            '                    "$.q4_promotion_record_identity_or_na: L4 PROMOTE requires "\n'
            '                    "concrete Q4 promotion evidence"'
        ),
        '                "$.aggregate_resource_cost.material_result_count: must equal material_results length"': (
            '                "$.aggregate_resource_cost.material_result_count: must equal "\n'
            '                "material_results length"'
        ),
        '                    "$.governed_effects.PAID_COMPUTE: positive paid cost requires explicit true declaration"': (
            '                    "$.governed_effects.PAID_COMPUTE: positive paid cost requires "\n'
            '                    "explicit true declaration"'
        ),
        '            "$.governed_effects: external-effect resource class requires at least one true governed effect"': (
            '            "$.governed_effects: external-effect resource class requires at least "\n'
            '            "one true governed effect"'
        ),
        '                    "$.external_effect_authority.authority_id: must be a path-safe canonical binding id"': (
            '                    "$.external_effect_authority.authority_id: must be a path-safe "\n'
            '                    "canonical binding id"'
        ),
        '                            "$.external_effect_authority.authority_id: canonical record identity mismatch"': (
            '                            "$.external_effect_authority.authority_id: canonical record "\n'
            '                            "identity mismatch"'
        ),
        '                            "$.external_effect_authority: canonical authority status must be AUTHORIZED_CANONICAL"': (
            '                            "$.external_effect_authority: canonical authority status must "\n'
            '                            "be AUTHORIZED_CANONICAL"'
        ),
        '                            "$.external_effect_authority: canonical authority task_id must match governing_task_id"': (
            '                            "$.external_effect_authority: canonical authority task_id must "\n'
            '                            "match governing_task_id"'
        ),
        '                            "$.external_effect_authority: canonical strongest effect must be declared true"': (
            '                            "$.external_effect_authority: canonical strongest effect must "\n'
            '                            "be declared true"'
        ),
        '                        errors.append("$.external_effect_authority: canonical authority scope is invalid")': (
            '                        errors.append(\n'
            '                            "$.external_effect_authority: canonical authority scope is invalid"\n'
            '                        )'
        ),
        '                                "$.external_effect_authority: canonical authority campaign scope mismatch"': (
            '                                "$.external_effect_authority: canonical authority campaign "\n'
            '                                "scope mismatch"'
        ),
        '                                "$.external_effect_authority: canonical authority ladder scope mismatch"': (
            '                                "$.external_effect_authority: canonical authority ladder "\n'
            '                                "scope mismatch"'
        ),
        '                                "$.external_effect_authority: canonical authority scope misses declared effect"': (
            '                                "$.external_effect_authority: canonical authority scope misses "\n'
            '                                "declared effect"'
        ),
        '                            "$.external_effect_authority: canonical authority lacks research resource ceilings"': (
            '                            "$.external_effect_authority: canonical authority lacks research "\n'
            '                            "resource ceilings"'
        ),
        '                                        f"$.budget.{field}: exceeds resolved canonical authority ceiling"': (
            '                                        f"$.budget.{field}: exceeds resolved canonical "\n'
            '                                        "authority ceiling"'
        ),
    }
    for old, new in replacements.items():
        replace_once(SCHEMAS, old, new)


def harden_tests() -> None:
    replace_once(TESTS, "from copy import deepcopy\n", "")
    replace_once(
        TESTS,
        "def _write_promoted_chain(root: Path, through_index: int) -> tuple[list[dict[str, object]], list[str]]:\n",
        "def _write_promoted_chain(\n"
        "    root: Path, through_index: int\n"
        ") -> tuple[list[dict[str, object]], list[str]]:\n",
    )


def verify_line_lengths() -> None:
    offenders: list[str] = []
    for path in (SCHEMAS, TESTS):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if len(line) > 100:
                offenders.append(f"{path}:{lineno}:{len(line)}:{line}")
    if offenders:
        raise SystemExit("remaining >100-character lines:\n" + "\n".join(offenders))


def main() -> None:
    harden_schemas()
    harden_tests()
    verify_line_lengths()


if __name__ == "__main__":
    main()
