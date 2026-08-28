from __future__ import annotations

from pathlib import Path


source = Path("src/mstr_qualify/schemas.py")
text = source.read_text(encoding="utf-8")
anchor = '    failure_distribution = instance.get("failure_distribution")\n'
insertion = '''    structural_features = instance.get("structural_features")
    if isinstance(structural_features, dict):
        for key, value in structural_features.items():
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and not math.isfinite(float(value))
            ):
                errors.append(
                    f"$.structural_features[{key!r}]: numeric value must be finite"
                )

    failure_distribution = instance.get("failure_distribution")
'''
if text.count(anchor) != 1:
    raise SystemExit("B020 structural-feature insertion anchor is not unique")
source.write_text(text.replace(anchor, insertion, 1), encoding="utf-8")

test_path = Path("tests/contract/test_difficulty_calibration_contract.py")
tests = test_path.read_text(encoding="utf-8")
test_anchor = '''def test_b020_non_finite_probability_fails_closed() -> None:
    value = fixture()
    value["estimated_solve_probability"] = math.nan
    assert any("must be finite" in item for item in errors(value))


'''
test_insertion = test_anchor + '''def test_b020_non_finite_structural_numeric_feature_fails_closed() -> None:
    for non_finite in (math.nan, math.inf, -math.inf):
        value = fixture()
        value["structural_features"]["numeric_probe"] = non_finite
        assert any("numeric value must be finite" in item for item in errors(value))


'''
if tests.count(test_anchor) != 1:
    raise SystemExit("B020 structural-feature test anchor is not unique")
test_path.write_text(tests.replace(test_anchor, test_insertion, 1), encoding="utf-8")

evidence_path = Path("evidence/mstr-000b/B020-difficulty-contract.md")
evidence = evidence_path.read_text(encoding="utf-8")
evidence_anchor = (
    "`structural_features` is a non-empty flat descriptor map. B020 records evidence shape only; "
    "it does not prescribe a learned feature extractor, execute a student model, or calibrate a "
    "real checkpoint.\n"
)
evidence_replacement = (
    "`structural_features` is a non-empty flat descriptor map. Numeric feature values must be "
    "finite; `NaN` and infinities fail closed. B020 records evidence shape only; it does not "
    "prescribe a learned feature extractor, execute a student model, or calibrate a real "
    "checkpoint.\n"
)
if evidence.count(evidence_anchor) != 1:
    raise SystemExit("B020 evidence hardening anchor is not unique")
evidence_path.write_text(evidence.replace(evidence_anchor, evidence_replacement, 1), encoding="utf-8")
