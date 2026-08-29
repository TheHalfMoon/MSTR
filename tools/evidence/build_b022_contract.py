from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path.cwd()

RUNTIME_SCHEMA = ROOT / "schemas" / "mstr-verifier-health-v0.schema.json"
DESIGN_SCHEMA = (
    ROOT
    / "specs"
    / "002-code-model-supremacy-foundation"
    / "contracts"
    / "mstr-verifier-health-v0.schema.json"
)
VALID_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "valid"
    / "mstr-verifier-health-v0.json"
)
INVALID_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "invalid"
    / "mstr-verifier-health-v0.json"
)
CONTRACT_TEST = ROOT / "tests" / "contract" / "test_verifier_health_contract.py"
EVIDENCE = ROOT / "evidence" / "mstr-000b" / "B022-verifier-health.md"
SCHEMAS_PY = ROOT / "src" / "mstr_qualify" / "schemas.py"
CLI_PY = ROOT / "src" / "mstr_qualify" / "cli.py"
SCHEMA_TEST = ROOT / "tests" / "contract" / "test_schemas.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match in {path}: found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


schema = {
    "$defs": {
        "evaluator_hash": {
            "additionalProperties": False,
            "properties": {
                "path": {"minLength": 1, "maxLength": 512, "type": "string"},
                "sha256": {
                    "pattern": "^[0-9a-f]{64}$",
                    "type": "string",
                },
            },
            "required": ["path", "sha256"],
            "type": "object",
        },
        "mutation_result": {
            "additionalProperties": False,
            "properties": {
                "mutation_id": {"minLength": 1, "maxLength": 256, "type": "string"},
                "shortcut_class": {
                    "enum": [
                        "DELETE_TESTS",
                        "WEAKEN_ASSERTIONS",
                        "HARDCODE_OUTPUT",
                        "MODIFY_EVALUATOR",
                        "FUTURE_HISTORY_READ",
                        "CACHED_SOLUTION_RECOVERY",
                        "SPOOF_COMMAND_OUTPUT",
                        "OTHER",
                    ]
                },
                "expected_rejection": {"type": "boolean"},
                "observed_rejection": {"type": "boolean"},
                "evidence_identity": {
                    "minLength": 1,
                    "maxLength": 512,
                    "type": "string",
                },
            },
            "required": [
                "mutation_id",
                "shortcut_class",
                "expected_rejection",
                "observed_rejection",
                "evidence_identity",
            ],
            "type": "object",
        },
        "leakage_check": {
            "additionalProperties": False,
            "properties": {
                "check_id": {"minLength": 1, "maxLength": 256, "type": "string"},
                "leakage_class": {
                    "enum": [
                        "FUTURE_HISTORY",
                        "HIDDEN_TEST",
                        "BENCHMARK_SOLUTION",
                        "CACHED_SOLUTION",
                        "PUBLIC_SOLUTION",
                        "OTHER",
                    ]
                },
                "status": {"enum": ["CLEAR", "DETECTED", "NOT_APPLICABLE"]},
                "evidence_identity": {
                    "minLength": 1,
                    "maxLength": 512,
                    "type": "string",
                },
            },
            "required": ["check_id", "leakage_class", "status", "evidence_identity"],
            "type": "object",
        },
        "disagreement_signal": {
            "additionalProperties": False,
            "properties": {
                "signal_id": {"minLength": 1, "maxLength": 256, "type": "string"},
                "left_evidence_identity": {
                    "minLength": 1,
                    "maxLength": 512,
                    "type": "string",
                },
                "right_evidence_identity": {
                    "minLength": 1,
                    "maxLength": 512,
                    "type": "string",
                },
                "status": {"enum": ["AGREE", "DISAGREE", "INDETERMINATE"]},
            },
            "required": [
                "signal_id",
                "left_evidence_identity",
                "right_evidence_identity",
                "status",
            ],
            "type": "object",
        },
        "stage_eligibility": {
            "additionalProperties": False,
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "admission_class": {"const": "CLEAN_POSITIVE_ELIGIBLE"}
                        },
                        "required": ["admission_class"],
                    },
                    "then": {
                        "properties": {"reason_codes": {"maxItems": 0}}
                    },
                    "else": {
                        "properties": {"reason_codes": {"minItems": 1}}
                    },
                }
            ],
            "properties": {
                "stage_id": {"minLength": 1, "maxLength": 256, "type": "string"},
                "admission_class": {
                    "enum": [
                        "CLEAN_POSITIVE_ELIGIBLE",
                        "RESEARCH_DIAGNOSTIC_ONLY",
                        "BLOCKED",
                    ]
                },
                "reason_codes": {
                    "items": {"minLength": 1, "maxLength": 128, "type": "string"},
                    "type": "array",
                    "uniqueItems": True,
                },
            },
            "required": ["stage_id", "admission_class", "reason_codes"],
            "type": "object",
        },
    },
    "$id": "https://mstr.local/schemas/mstr-verifier-health-v0.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "additionalProperties": False,
    "allOf": [
        {
            "if": {
                "properties": {
                    "health_class": {"enum": ["PARTIAL", "DISAGREEMENT"]}
                },
                "required": ["health_class"],
            },
            "then": {
                "properties": {
                    "training_stage_eligibility": {
                        "items": {
                            "properties": {
                                "admission_class": {
                                    "enum": ["RESEARCH_DIAGNOSTIC_ONLY", "BLOCKED"]
                                }
                            }
                        }
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "health_class": {"enum": ["BROKEN", "LEAKED", "TAMPERED"]}
                },
                "required": ["health_class"],
            },
            "then": {
                "properties": {
                    "training_stage_eligibility": {
                        "items": {
                            "properties": {
                                "admission_class": {"const": "BLOCKED"}
                            }
                        }
                    }
                }
            },
        },
    ],
    "properties": {
        "schema_version": {"const": "mstr.verifier-health.v0"},
        "verifier_health_id": {"minLength": 1, "maxLength": 512, "type": "string"},
        "task_identity": {"minLength": 1, "maxLength": 512, "type": "string"},
        "verifier_manifest_id": {"minLength": 1, "maxLength": 512, "type": "string"},
        "evaluator_hashes": {
            "items": {"$ref": "#/$defs/evaluator_hash"},
            "minItems": 1,
            "type": "array",
            "uniqueItems": True,
        },
        "protected_paths": {
            "items": {"minLength": 1, "maxLength": 512, "type": "string"},
            "minItems": 1,
            "type": "array",
            "uniqueItems": True,
        },
        "protected_path_integrity": {"enum": ["PASS", "FAIL"]},
        "reference_oracle_status": {"enum": ["PASS", "FAIL", "NOT_APPLICABLE"]},
        "noop_fail_status": {"enum": ["PASS", "FAIL", "NOT_APPLICABLE"]},
        "known_bad_fail_status": {"enum": ["PASS", "FAIL", "NOT_APPLICABLE"]},
        "mutation_results": {
            "items": {"$ref": "#/$defs/mutation_result"},
            "minItems": 1,
            "type": "array",
            "uniqueItems": True,
        },
        "generated_test_independence": {
            "enum": [
                "INDEPENDENT",
                "PARTIAL",
                "NOT_INDEPENDENT",
                "NOT_APPLICABLE",
                "UNRESOLVED",
            ]
        },
        "leakage_checks": {
            "items": {"$ref": "#/$defs/leakage_check"},
            "minItems": 1,
            "type": "array",
            "uniqueItems": True,
        },
        "disagreement_signals": {
            "items": {"$ref": "#/$defs/disagreement_signal"},
            "minItems": 1,
            "type": "array",
            "uniqueItems": True,
        },
        "health_class": {
            "enum": [
                "HEALTHY",
                "PARTIAL",
                "DISAGREEMENT",
                "BROKEN",
                "LEAKED",
                "TAMPERED",
            ]
        },
        "training_stage_eligibility": {
            "items": {"$ref": "#/$defs/stage_eligibility"},
            "minItems": 1,
            "type": "array",
            "uniqueItems": True,
        },
    },
    "required": [
        "schema_version",
        "verifier_health_id",
        "task_identity",
        "verifier_manifest_id",
        "evaluator_hashes",
        "protected_paths",
        "protected_path_integrity",
        "reference_oracle_status",
        "noop_fail_status",
        "known_bad_fail_status",
        "mutation_results",
        "generated_test_independence",
        "leakage_checks",
        "disagreement_signals",
        "health_class",
        "training_stage_eligibility",
    ],
    "title": "MSTR Verifier Health v0",
    "type": "object",
}

schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
RUNTIME_SCHEMA.write_text(schema_text, encoding="utf-8")
DESIGN_SCHEMA.write_text(schema_text, encoding="utf-8")

valid = {
    "schema_version": "mstr.verifier-health.v0",
    "verifier_health_id": "vh-fixture-healthy-v0",
    "task_identity": "fixture-task/verifier-health",
    "verifier_manifest_id": "fixture-verifier-manifest-v0",
    "evaluator_hashes": [
        {
            "path": "tests/verifier.py",
            "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        }
    ],
    "protected_paths": ["tests/verifier.py"],
    "protected_path_integrity": "PASS",
    "reference_oracle_status": "PASS",
    "noop_fail_status": "PASS",
    "known_bad_fail_status": "PASS",
    "mutation_results": [
        {
            "mutation_id": "delete-tests",
            "shortcut_class": "DELETE_TESTS",
            "expected_rejection": True,
            "observed_rejection": True,
            "evidence_identity": "fixture-mutation-delete-tests",
        }
    ],
    "generated_test_independence": "INDEPENDENT",
    "leakage_checks": [
        {
            "check_id": "future-history",
            "leakage_class": "FUTURE_HISTORY",
            "status": "CLEAR",
            "evidence_identity": "fixture-leakage-future-history",
        }
    ],
    "disagreement_signals": [
        {
            "signal_id": "existing-vs-targeted",
            "left_evidence_identity": "fixture-existing-tests",
            "right_evidence_identity": "fixture-targeted-tests",
            "status": "AGREE",
        }
    ],
    "health_class": "HEALTHY",
    "training_stage_eligibility": [
        {
            "stage_id": "MSTR-002",
            "admission_class": "CLEAN_POSITIVE_ELIGIBLE",
            "reason_codes": [],
        }
    ],
}
VALID_FIXTURE.write_text(json.dumps(valid, indent=2, sort_keys=True) + "\n", encoding="utf-8")

invalid = json.loads(json.dumps(valid))
invalid["health_class"] = "BROKEN"
INVALID_FIXTURE.write_text(
    json.dumps(invalid, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

replace_once(
    SCHEMAS_PY,
    '    # MSTR-000B B020: checkpoint-relative difficulty calibration contract.\n'
    '    "mstr-difficulty-calibration-v0": "mstr-difficulty-calibration-v0.schema.json",\n',
    '    # MSTR-000B B020: checkpoint-relative difficulty calibration contract.\n'
    '    "mstr-difficulty-calibration-v0": "mstr-difficulty-calibration-v0.schema.json",\n'
    '    # MSTR-000B B022: verifier-health evidence contract.\n'
    '    "mstr-verifier-health-v0": "mstr-verifier-health-v0.schema.json",\n',
)

replace_once(
    CLI_PY,
    '    # MSTR-000B B020 checkpoint-relative difficulty calibration contract.\n'
    '    "mstr.difficulty-calibration.v0": "mstr-difficulty-calibration-v0",\n',
    '    # MSTR-000B B020 checkpoint-relative difficulty calibration contract.\n'
    '    "mstr.difficulty-calibration.v0": "mstr-difficulty-calibration-v0",\n'
    '    # MSTR-000B B022 verifier-health evidence contract.\n'
    '    "mstr.verifier-health.v0": "mstr-verifier-health-v0",\n',
)

replace_once(
    SCHEMA_TEST,
    '    "mstr-difficulty-calibration-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-difficulty-calibration-v0.schema.json"\n'
    '    ),\n',
    '    "mstr-difficulty-calibration-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-difficulty-calibration-v0.schema.json"\n'
    '    ),\n'
    '    "mstr-verifier-health-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-verifier-health-v0.schema.json"\n'
    '    ),\n',
)

CONTRACT_TEST.write_text(
    textwrap.dedent(
        '''\
        from __future__ import annotations

        import copy
        import json
        from pathlib import Path

        import pytest

        from mstr_qualify.cli import _SCHEMA_VERSION_TO_SCHEMA_NAME
        from mstr_qualify.schemas import SCHEMA_FILES, validate_instance, validation_errors

        ROOT = Path(__file__).resolve().parents[2]
        SCHEMA_NAME = "mstr-verifier-health-v0"
        VERSION = "mstr.verifier-health.v0"
        VALID = ROOT / "tests" / "fixtures" / "schemas" / "valid" / f"{SCHEMA_NAME}.json"
        INVALID = ROOT / "tests" / "fixtures" / "schemas" / "invalid" / f"{SCHEMA_NAME}.json"


        def fixture() -> dict[str, object]:
            decoded = json.loads(VALID.read_text(encoding="utf-8"))
            assert isinstance(decoded, dict)
            return decoded


        def errors(value: object) -> tuple[str, ...]:
            return validation_errors(SCHEMA_NAME, value)


        def stage(record: dict[str, object]) -> dict[str, object]:
            stages = record["training_stage_eligibility"]
            assert isinstance(stages, list)
            value = stages[0]
            assert isinstance(value, dict)
            return value


        def test_b022_schema_is_registered_for_offline_validation() -> None:
            assert SCHEMA_FILES[SCHEMA_NAME] == "mstr-verifier-health-v0.schema.json"
            assert _SCHEMA_VERSION_TO_SCHEMA_NAME[VERSION] == SCHEMA_NAME


        def test_b022_design_and_runtime_schemas_are_byte_identical() -> None:
            runtime = ROOT / "schemas" / "mstr-verifier-health-v0.schema.json"
            design = (
                ROOT
                / "specs"
                / "002-code-model-supremacy-foundation"
                / "contracts"
                / "mstr-verifier-health-v0.schema.json"
            )
            assert runtime.read_bytes() == design.read_bytes()


        def test_b022_valid_healthy_fixture_passes() -> None:
            validate_instance(SCHEMA_NAME, fixture())


        def test_b022_invalid_clean_positive_broken_fixture_fails_closed() -> None:
            invalid = json.loads(INVALID.read_text(encoding="utf-8"))
            assert errors(invalid)


        @pytest.mark.parametrize(
            "field",
            [
                "evaluator_hashes",
                "protected_paths",
                "protected_path_integrity",
                "reference_oracle_status",
                "noop_fail_status",
                "known_bad_fail_status",
                "mutation_results",
                "generated_test_independence",
                "leakage_checks",
                "disagreement_signals",
                "health_class",
                "training_stage_eligibility",
            ],
        )
        def test_b022_required_verifier_health_surface_fails_closed_when_missing(field: str) -> None:
            record = fixture()
            del record[field]
            assert errors(record)


        def test_b022_evaluator_hash_must_be_sha256() -> None:
            record = fixture()
            hashes = record["evaluator_hashes"]
            assert isinstance(hashes, list)
            item = hashes[0]
            assert isinstance(item, dict)
            item["sha256"] = "not-a-sha256"
            assert errors(record)


        @pytest.mark.parametrize(
            "health_class",
            ["PARTIAL", "DISAGREEMENT"],
        )
        def test_b022_partial_or_disagreement_cannot_claim_clean_positive(
            health_class: str,
        ) -> None:
            record = fixture()
            record["health_class"] = health_class
            assert errors(record)


        @pytest.mark.parametrize(
            "health_class",
            ["BROKEN", "LEAKED", "TAMPERED"],
        )
        def test_b022_blocking_health_classes_require_blocked_stage(
            health_class: str,
        ) -> None:
            record = fixture()
            record["health_class"] = health_class
            current_stage = stage(record)
            current_stage["admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
            current_stage["reason_codes"] = ["not-clean-positive"]
            assert errors(record)


        @pytest.mark.parametrize(
            "health_class",
            ["PARTIAL", "DISAGREEMENT"],
        )
        def test_b022_partial_or_disagreement_may_be_research_diagnostic(
            health_class: str,
        ) -> None:
            record = fixture()
            record["health_class"] = health_class
            current_stage = stage(record)
            current_stage["admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
            current_stage["reason_codes"] = ["health-below-clean-positive-threshold"]
            validate_instance(SCHEMA_NAME, record)


        @pytest.mark.parametrize(
            "health_class",
            ["BROKEN", "LEAKED", "TAMPERED"],
        )
        def test_b022_blocking_health_classes_may_only_be_blocked(
            health_class: str,
        ) -> None:
            record = fixture()
            record["health_class"] = health_class
            current_stage = stage(record)
            current_stage["admission_class"] = "BLOCKED"
            current_stage["reason_codes"] = ["verifier-health-blocking"]
            validate_instance(SCHEMA_NAME, record)


        def test_b022_non_clean_stage_requires_reason_code() -> None:
            record = fixture()
            record["health_class"] = "PARTIAL"
            current_stage = stage(record)
            current_stage["admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
            assert errors(record)


        def test_b022_clean_positive_stage_rejects_reason_codes() -> None:
            record = fixture()
            current_stage = stage(record)
            current_stage["reason_codes"] = ["unexpected"]
            assert errors(record)


        @pytest.mark.parametrize(
            ("field", "value"),
            [
                ("reference_oracle_status", "NOT_APPLICABLE"),
                ("noop_fail_status", "NOT_APPLICABLE"),
                ("known_bad_fail_status", "NOT_APPLICABLE"),
                ("generated_test_independence", "NOT_APPLICABLE"),
            ],
        )
        def test_b022_explicit_not_applicable_is_supported_where_defined(
            field: str,
            value: str,
        ) -> None:
            record = fixture()
            record[field] = value
            validate_instance(SCHEMA_NAME, record)


        def test_b022_unknown_fields_fail_closed() -> None:
            record = fixture()
            record["training_authorized"] = True
            assert errors(record)


        def test_b022_schema_freezes_exact_health_classes() -> None:
            schema = json.loads(
                (ROOT / "schemas" / "mstr-verifier-health-v0.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            assert schema["properties"]["health_class"]["enum"] == [
                "HEALTHY",
                "PARTIAL",
                "DISAGREEMENT",
                "BROKEN",
                "LEAKED",
                "TAMPERED",
            ]


        def test_b022_entry_provenance_and_authority_boundary() -> None:
            evidence = (ROOT / "evidence" / "mstr-000b" / "B022-verifier-health.md").read_text(
                encoding="utf-8"
            )
            assert "ENTRY_GATE_TASK = B022" in evidence
            assert "ENTRY_GATE_CANONICAL_MAIN = 127fd5fd1a5a6f1843f207a0272664ae8cb129f4" in evidence
            assert "ENTRY_GATE_RUN = 33245383036" in evidence
            assert "ENTRY_GATE_JOB = 99081833546" in evidence
            assert "ENTRY_GATE_ELIGIBLE = true" in evidence
            assert "ENTRY_GATE_DRIFT = clean" in evidence
            assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
            assert "MODEL_EXECUTION = NONE" in evidence
            assert "VERIFIER_EVALUATOR_EXECUTION = NONE" in evidence
            assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
            assert "B023_VERIFIER_HEALTH_EVALUATOR_AUTHORITY = NONE" in evidence
            assert "B024_TEST_GENERATION_CURRICULUM_AUTHORITY = NONE" in evidence


        def test_b022_fixture_mutations_do_not_change_input_helper() -> None:
            first = fixture()
            second = copy.deepcopy(first)
            second["health_class"] = "PARTIAL"
            assert first["health_class"] == "HEALTHY"
        '''
    ),
    encoding="utf-8",
)

EVIDENCE.write_text(
    textwrap.dedent(
        '''\
        # B022 — VerifierHealthRecord Contract Evidence

        **Task:** `B022`
        **State:** `IMPLEMENTATION_ACTIVE`
        **Canonical entry main:** `127fd5fd1a5a6f1843f207a0272664ae8cb129f4`

        ## Canonical Entry Provenance

        ```text
        ENTRY_GATE_TASK = B022
        ENTRY_GATE_CANONICAL_MAIN = 127fd5fd1a5a6f1843f207a0272664ae8cb129f4
        ENTRY_GATE_RUN = 33245383036
        ENTRY_GATE_JOB = 99081833546
        ENTRY_GATE_ELIGIBLE = true
        ENTRY_GATE_DRIFT = clean
        B014_PREREQUISITE = COMPLETE_CANONICAL
        B021_STATE = COMPLETE_CANONICAL
        B011_STATE = BLOCKED_EXTERNAL_AUTHORITY_UNSATISFIED
        ```

        The entry gate ran the canonical task validator against the exact immutable `main`, proved clean MSTR-000B task drift, re-proved the B014 prerequisite, preserved B021 as terminal, preserved B011 as externally blocked, and ran the repository quality gates before B022 mutation.

        ## Frozen Contract Surface

        `mstr.verifier-health.v0` records verifier evidence without implementing the B023 evaluator/classifier. The record requires:

        - exact verifier-health, task, and verifier-manifest identities;
        - evaluator path + SHA-256 bindings;
        - protected evaluator paths and their integrity status;
        - reference-oracle, no-op rejection, and known-bad rejection status with explicit `NOT_APPLICABLE` where the check does not apply;
        - mutation/reward-shortcut probes with expected and observed rejection evidence;
        - generated-test independence state;
        - leakage checks and disagreement signals;
        - one of `HEALTHY`, `PARTIAL`, `DISAGREEMENT`, `BROKEN`, `LEAKED`, or `TAMPERED`;
        - stage-level verifier-health admission posture.

        The contract freezes the Data Constitution threshold boundary: `PARTIAL` and `DISAGREEMENT` cannot claim clean-positive eligibility, while `BROKEN`, `LEAKED`, and `TAMPERED` must be blocked. B022 does not derive the health class from signals; controlled classification behavior belongs to B023.

        Runtime and design-source schemas are byte-identical. Dedicated valid/invalid fixtures exercise healthy clean-positive admission and fail-closed rejection of a broken verifier that falsely claims clean-positive eligibility.

        ## Authority Boundary

        ```text
        MODEL_WEIGHT_ACCESS = NONE
        MODEL_EXECUTION = NONE
        VERIFIER_EVALUATOR_EXECUTION = NONE
        TEACHER_API_EXECUTION = NONE
        PAID_MODEL_API = NONE
        PAID_COMPUTE = NONE
        NETWORK_MODEL_OR_TEACHER_CALL = NONE
        LARGE_DATASET_INGESTION = NONE
        PRIVATE_USER_DATA_INGESTION = NONE
        PRODUCTION_TRACE_INGESTION = NONE
        WEIGHT_CHANGING_TRAINING = NONE
        LARGE_SCALE_RL = NONE
        PRODUCTION_RELEASE = NONE
        B023_VERIFIER_HEALTH_EVALUATOR_AUTHORITY = NONE
        B024_TEST_GENERATION_CURRICULUM_AUTHORITY = NONE
        B022_AUTHORITY = VERIFIER_HEALTH_CONTRACT_AND_FIXTURES_ONLY
        ```

        This task freezes a record contract only. It does not execute real verifiers, classify controlled fixtures, admit training data, generate tests, access model weights, run a model, or authorize training.
        '''
    ),
    encoding="utf-8",
)
