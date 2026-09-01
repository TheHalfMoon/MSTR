"""Strict local JSON Schema loading and validation for MSTR qualification records.

T004 deliberately supports only a fixed set of repository-local schemas. Remote
references are rejected before a validator is constructed so schema validation
cannot become an implicit network boundary.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from .errors import SchemaValidationError

SCHEMA_FILES: Mapping[str, str] = {
    "candidate-record": "candidate-record.schema.json",
    "task-manifest": "task-manifest.schema.json",
    "run-evidence": "run-evidence.schema.json",
    "interaction-contract": "interaction-contract.schema.json",
    # T027 weight-access preparation manifest. No remote refs; no external
    # network boundary; validated fully offline once registered.
    "weight-access-manifest": "weight-access-manifest.schema.json",
    # Zero-large-artifact founder-environment storage amendment (T028).
    "storage-amendment": "storage-amendment.schema.json",
    # MSTR-000A A001/A002: loop contract and run-event schemas.
    "mstr-loop-contract-v0": "mstr-loop-contract-v0.schema.json",
    "mstr-run-event-v0": "mstr-run-event-v0.schema.json",
    # MSTR-000A A010: evidence-derived WePLD routing capability profile.
    "mstr-capability-profile-v0": "mstr-capability-profile-v0.schema.json",
    # MSTR-000A A011: environment/setup/verifier identities and effect boundaries.
    "mstr-environment-manifest-v0": "mstr-environment-manifest-v0.schema.json",
    "mstr-setup-manifest-v0": "mstr-setup-manifest-v0.schema.json",
    "mstr-verifier-manifest-v0": "mstr-verifier-manifest-v0.schema.json",
    # MSTR-000A A015: Direction-to-Done task identity and hidden acceptance boundary.
    "mstr-direction-task-v0": "mstr-direction-task-v0.schema.json",
    # MSTR-000A A017: failure-inclusive trajectory and training-admission contract.
    "mstr-trajectory-manifest-v0": "mstr-trajectory-manifest-v0.schema.json",
    # MSTR-000B B001: machine-readable task graph and eligibility result contracts.
    "mstr-task-node-v0": "mstr-task-node-v0.schema.json",
    "mstr-task-eligibility-v0": "mstr-task-eligibility-v0.schema.json",
    # MSTR-000B B014: fail-closed Data Constitution contract.
    "mstr-data-constitution-v0": "mstr-data-constitution-v0.schema.json",
    # MSTR-000B B016: software-evolution lineage and future-history boundary.
    "mstr-software-evolution-record-v0": "mstr-software-evolution-record-v0.schema.json",
    # MSTR-000B B018: execution-filtered student self-alignment contract.
    "mstr-self-alignment-generation-v0": "mstr-self-alignment-generation-v0.schema.json",
    # MSTR-000B B019: bounded teacher-rescue record contract.
    "mstr-teacher-rescue-record-v0": "mstr-teacher-rescue-record-v0.schema.json",
    # MSTR-000B B020: checkpoint-relative difficulty calibration contract.
    "mstr-difficulty-calibration-v0": "mstr-difficulty-calibration-v0.schema.json",
    # MSTR-000B B022: verifier-health evidence contract.
    "mstr-verifier-health-v0": "mstr-verifier-health-v0.schema.json",
    # MSTR-000B B024: test-generation example and acceptance contract.
    "mstr-test-generation-example-v0": "mstr-test-generation-example-v0.schema.json",
    # MSTR-000B B025: greenfield/feature/synthesis task manifest contract.
    "mstr-greenfield-task-v0": "mstr-greenfield-task-v0.schema.json",
    # MSTR-000B B028: training-method preflight and fail-closed Q4 promotion.
    "mstr-training-method-cell-v0": "mstr-training-method-cell-v0.schema.json",
    "mstr-q4-promotion-v0": "mstr-q4-promotion-v0.schema.json",
}

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_DIR = _REPOSITORY_ROOT / "schemas"


def _walk_json(value: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def _reject_external_refs(schema: Mapping[str, Any]) -> None:
    for key, value in _walk_json(schema):
        if key != "$ref":
            continue
        if not isinstance(value, str):
            raise SchemaValidationError(
                "schema $ref values must be strings", code="schema.ref_type"
            )
        if not value.startswith("#"):
            raise SchemaValidationError(
                "external schema reference is prohibited",
                code="schema.external_ref",
                details={"ref": value},
            )


def load_schema(name: str, *, schema_dir: Path | None = None) -> dict[str, Any]:
    """Load and self-check one registered repository-local schema."""

    try:
        filename = SCHEMA_FILES[name]
    except KeyError as exc:
        allowed = ", ".join(sorted(SCHEMA_FILES))
        raise SchemaValidationError(
            "unknown schema",
            code="schema.unknown",
            details={"name": name, "allowed": allowed},
        ) from exc

    path = (schema_dir or DEFAULT_SCHEMA_DIR) / filename
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SchemaValidationError(
            "unable to read schema",
            code="schema.read",
            details={"name": name, "path": str(path)},
        ) from exc

    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(
            "schema is not valid JSON",
            code="schema.json",
            details={"name": name, "reason": exc.msg},
        ) from exc

    if not isinstance(schema, dict):
        raise SchemaValidationError(
            "schema must contain a JSON object",
            code="schema.root_type",
            details={"name": name},
        )

    _reject_external_refs(schema)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise SchemaValidationError(
            "schema is not valid Draft 2020-12 JSON Schema",
            code="schema.meta",
            details={"name": name, "reason": exc.message},
        ) from exc
    return schema


def _format_validation_error(error: ValidationError) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return f"{path}: {error.message}"


def _self_alignment_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B018 cross-field evidence bindings that JSON Schema cannot express."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    artifacts: dict[str, dict[str, Any]] = {}

    def register_artifact(value: Any) -> None:
        if not isinstance(value, dict):
            return
        artifact_id = value.get("artifact_id")
        if not isinstance(artifact_id, str):
            return
        if artifact_id in artifacts:
            errors.append(f"$.generated_artifacts: duplicate artifact_id {artifact_id!r}")
            return
        artifacts[artifact_id] = value

    register_artifact(instance.get("generated_task"))
    for collection in ("generated_solutions", "generated_tests"):
        values = instance.get(collection)
        if isinstance(values, list):
            for value in values:
                register_artifact(value)

    def check_artifact_bindings(field: str, nested_field: str) -> None:
        raw_bindings = instance.get(field)
        if not isinstance(raw_bindings, list):
            return
        bindings: dict[str, dict[str, Any]] = {}
        for index, binding in enumerate(raw_bindings):
            if not isinstance(binding, dict):
                continue
            artifact_id = binding.get("artifact_id")
            if not isinstance(artifact_id, str):
                continue
            if artifact_id in bindings:
                errors.append(f"$.{field}[{index}]: duplicate artifact binding {artifact_id!r}")
                continue
            bindings[artifact_id] = binding
        if set(bindings) != set(artifacts):
            errors.append(f"$.{field}: bindings must exactly cover generated artifact ids")
        for artifact_id in sorted(set(bindings) & set(artifacts)):
            if bindings[artifact_id].get(nested_field) != artifacts[artifact_id].get(nested_field):
                errors.append(
                    f"$.{field}: binding for {artifact_id!r} does not match artifact {nested_field}"
                )

    check_artifact_bindings("generated_artifact_provenance", "provenance")
    check_artifact_bindings("generated_artifact_rights_decisions", "rights_decision")

    raw_execution = instance.get("execution_results")
    expected_execution = {
        artifact_id: artifact
        for artifact_id, artifact in artifacts.items()
        if artifact.get("artifact_kind") in {"SOLUTION", "TEST"}
    }
    if isinstance(raw_execution, list):
        bindings: dict[str, dict[str, Any]] = {}
        for index, binding in enumerate(raw_execution):
            if not isinstance(binding, dict):
                continue
            artifact_id = binding.get("artifact_id")
            if not isinstance(artifact_id, str):
                continue
            if artifact_id in bindings:
                errors.append(f"$.execution_results[{index}]: duplicate binding {artifact_id!r}")
                continue
            bindings[artifact_id] = binding
        if set(bindings) != set(expected_execution):
            errors.append("$.execution_results: must exactly cover executable artifact ids")
        environment_identity = instance.get("environment_identity")
        for artifact_id in sorted(set(bindings) & set(expected_execution)):
            binding = bindings[artifact_id]
            artifact = expected_execution[artifact_id]
            if binding.get("execution_result") != artifact.get("execution_result"):
                errors.append(
                    f"$.execution_results: {artifact_id!r} does not match artifact execution_result"
                )
            if binding.get("environment_identity") != environment_identity:
                errors.append(
                    f"$.execution_results: {artifact_id!r} does not match environment_identity"
                )

    student = instance.get("student_model_identity")
    difficulty = instance.get("difficulty_record")
    if isinstance(student, dict) and isinstance(difficulty, dict):
        if difficulty.get("student_model_identity") != student:
            errors.append(
                "$.difficulty_record.student_model_identity: must match student_model_identity"
            )
        if difficulty.get("harness_profile_id") != student.get("harness_profile_id"):
            errors.append(
                "$.difficulty_record.harness_profile_id: must match student harness_profile_id"
            )
        if difficulty.get("sampling_identity") != student.get("sampling_identity"):
            errors.append(
                "$.difficulty_record.sampling_identity: must match exact student sampling_identity"
            )

    return tuple(sorted(errors))


def _teacher_rescue_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B019 output bindings and external-effect authority semantics."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    outputs: dict[str, dict[str, Any]] = {}
    raw_outputs = instance.get("teacher_outputs")
    if isinstance(raw_outputs, list):
        for index, output in enumerate(raw_outputs):
            if not isinstance(output, dict):
                continue
            output_id = output.get("output_id")
            if not isinstance(output_id, str):
                continue
            if output_id in outputs:
                errors.append(f"$.teacher_outputs[{index}]: duplicate output_id {output_id!r}")
                continue
            outputs[output_id] = output

    def collect_bindings(field: str) -> dict[str, dict[str, Any]]:
        bindings: dict[str, dict[str, Any]] = {}
        raw = instance.get(field)
        if not isinstance(raw, list):
            return bindings
        for index, binding in enumerate(raw):
            if not isinstance(binding, dict):
                continue
            output_id = binding.get("output_id")
            if not isinstance(output_id, str):
                continue
            if output_id in bindings:
                errors.append(f"$.{field}[{index}]: duplicate output binding {output_id!r}")
                continue
            bindings[output_id] = binding
        return bindings

    for field in ("output_provenance", "output_rights_decisions"):
        bindings = collect_bindings(field)
        if set(bindings) != set(outputs):
            errors.append(f"$.{field}: bindings must exactly cover teacher output ids")

    expected_execution = {
        output_id
        for output_id, output in outputs.items()
        if output.get("execution_required") is True
    }
    execution_bindings = collect_bindings("independent_execution_results")
    if set(execution_bindings) != expected_execution:
        errors.append(
            "$.independent_execution_results: bindings must exactly cover "
            "execution-required teacher output ids"
        )

    cost = instance.get("cost_record")
    teacher = instance.get("teacher_identity")
    if isinstance(cost, dict):
        paid = cost.get("paid_cost_usd")
        network_used = cost.get("network_used") is True
        model_executed = cost.get("model_execution_occurred") is True
        authority = cost.get("external_effect_authority_identity")
        external_effect = (
            (isinstance(paid, (int, float)) and not isinstance(paid, bool) and paid > 0)
            or network_used
            or model_executed
        )
        if external_effect and not isinstance(authority, str):
            errors.append(
                "$.cost_record.external_effect_authority_identity: required when "
                "paid cost, network use, or model execution is recorded"
            )
        if not external_effect and authority is not None:
            errors.append(
                "$.cost_record.external_effect_authority_identity: must be null when "
                "no external effect is recorded"
            )
        if isinstance(teacher, dict):
            access_mode = teacher.get("access_mode")
            if access_mode == "REFERENCE_ONLY" and external_effect:
                errors.append(
                    "$.teacher_identity.access_mode: REFERENCE_ONLY cannot record "
                    "paid cost, network use, or model execution"
                )
            if access_mode == "REMOTE_API" and not (network_used and model_executed):
                errors.append(
                    "$.teacher_identity.access_mode: REMOTE_API requires recorded "
                    "network use and model execution"
                )
            if access_mode == "LOCAL_MODEL" and not model_executed:
                errors.append(
                    "$.teacher_identity.access_mode: LOCAL_MODEL requires recorded model execution"
                )

    return tuple(sorted(errors))


def _difficulty_calibration_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B020 checkpoint-relative identity and attempt-accounting semantics."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    attempts = instance.get("attempt_count")
    successes = instance.get("success_count")
    if (
        isinstance(attempts, int)
        and not isinstance(attempts, bool)
        and isinstance(successes, int)
        and not isinstance(successes, bool)
        and successes > attempts
    ):
        errors.append("$.success_count: cannot exceed attempt_count")

    probability = instance.get("estimated_solve_probability")
    if (
        isinstance(probability, (int, float))
        and not isinstance(probability, bool)
        and not math.isfinite(float(probability))
    ):
        errors.append("$.estimated_solve_probability: must be finite")

    student = instance.get("student_model_identity")
    if isinstance(student, dict):
        if instance.get("harness_profile_id") != student.get("harness_profile_id"):
            errors.append(
                "$.harness_profile_id: must match student_model_identity.harness_profile_id"
            )
        if instance.get("sampling_identity") != student.get("sampling_identity"):
            errors.append(
                "$.sampling_identity: must match student_model_identity.sampling_identity"
            )

    structural_features = instance.get("structural_features")
    if isinstance(structural_features, dict):
        for key, value in structural_features.items():
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and not math.isfinite(float(value))
            ):
                errors.append(f"$.structural_features[{key!r}]: numeric value must be finite")

    failure_distribution = instance.get("failure_distribution")
    if isinstance(failure_distribution, list):
        seen: set[str] = set()
        failure_total = 0
        countable = True
        for index, bucket in enumerate(failure_distribution):
            if not isinstance(bucket, dict):
                countable = False
                continue
            failure_class = bucket.get("failure_class")
            count = bucket.get("count")
            if isinstance(failure_class, str):
                if failure_class in seen:
                    errors.append(
                        "$.failure_distribution["
                        f"{index}]: duplicate failure_class {failure_class!r}"
                    )
                seen.add(failure_class)
            if isinstance(count, int) and not isinstance(count, bool) and count >= 0:
                failure_total += count
            else:
                countable = False
        if (
            countable
            and isinstance(attempts, int)
            and not isinstance(attempts, bool)
            and isinstance(successes, int)
            and not isinstance(successes, bool)
            and 0 <= successes <= attempts
            and failure_total != attempts - successes
        ):
            errors.append(
                "$.failure_distribution: counts must exactly cover attempt_count - success_count"
            )

    return tuple(sorted(errors))


def _task_specific_acceptance_binding(
    instance: Mapping[str, Any],
    patch: Mapping[str, Any],
    post: Mapping[str, Any],
    evidence_identity: str,
) -> str:
    """Bind independent B024 acceptance evidence to its exact acceptance context."""

    payload = {
        "environment_identity": post.get("environment_identity"),
        "execution_evidence_identity": post.get("evidence_identity"),
        "independent_acceptance_evidence_identity": evidence_identity,
        "revision": instance.get("fix_revision"),
        "task_identity": instance.get("task_identity"),
        "test_artifact_sha256": patch.get("test_artifact_sha256"),
        "verifier_manifest_id": post.get("verifier_manifest_id"),
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"{evidence_identity}|binding-sha256:{hashlib.sha256(encoded).hexdigest()}"


def _test_generation_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B024 cross-field behavioral and identity bindings."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    patch = instance.get("generated_test_patch")
    proof = instance.get("behavioral_proof")
    pre: dict[str, Any] | None = None
    post: dict[str, Any] | None = None
    if isinstance(patch, dict) and isinstance(proof, dict):
        artifact_sha = patch.get("test_artifact_sha256")
        if (
            proof.get("proof_kind") == "FAIL_BEFORE_PASS_AFTER"
            and instance.get("base_revision") == instance.get("fix_revision")
        ):
            errors.append(
                "$.fix_revision: FAIL_BEFORE_PASS_AFTER requires a revision "
                "distinct from base_revision"
            )
        raw_pre = proof.get("pre_fix_result")
        raw_post = proof.get("post_fix_result")
        if isinstance(raw_pre, dict) and isinstance(raw_post, dict):
            pre = raw_pre
            post = raw_post
            for label, result in (("pre_fix_result", pre), ("post_fix_result", post)):
                if result.get("task_identity") != instance.get("task_identity"):
                    errors.append(
                        f"$.behavioral_proof.{label}.task_identity: must match task_identity"
                    )
                if result.get("test_artifact_sha256") != artifact_sha:
                    errors.append(
                        f"$.behavioral_proof.{label}.test_artifact_sha256: "
                        "must match generated_test_patch.test_artifact_sha256"
                    )
            if pre.get("revision") != instance.get("base_revision"):
                errors.append(
                    "$.behavioral_proof.pre_fix_result.revision: must match base_revision"
                )
            if post.get("revision") != instance.get("fix_revision"):
                errors.append(
                    "$.behavioral_proof.post_fix_result.revision: must match fix_revision"
                )
            if pre.get("environment_identity") != post.get("environment_identity"):
                errors.append(
                    "$.behavioral_proof: pre/post environment_identity must match"
                )
            if pre.get("verifier_manifest_id") != post.get("verifier_manifest_id"):
                errors.append(
                    "$.behavioral_proof: pre/post verifier_manifest_id must match"
                )
            if proof.get("proof_kind") == "TASK_SPECIFIC_BEHAVIOR":
                raw_binding = proof.get("independent_acceptance_evidence_identity")
                evidence_identity: str | None = None
                if isinstance(raw_binding, str):
                    prefix, marker, _digest = raw_binding.rpartition("|binding-sha256:")
                    if marker and prefix and "|binding-sha256:" not in prefix:
                        evidence_identity = prefix
                expected_binding = (
                    _task_specific_acceptance_binding(
                        instance,
                        patch,
                        post,
                        evidence_identity,
                    )
                    if evidence_identity is not None
                    else None
                )
                if raw_binding != expected_binding:
                    errors.append(
                        "$.behavioral_proof.independent_acceptance_evidence_identity: "
                        "TASK_SPECIFIC_BEHAVIOR must preserve an independent evidence identity "
                        "and bind it to the exact task, fix revision, test artifact, environment, "
                        "verifier manifest, and execution evidence"
                    )

    if isinstance(patch, dict):
        changed_paths = patch.get("changed_paths")
        test_paths = patch.get("test_paths")
        if isinstance(changed_paths, list) and isinstance(test_paths, list):
            changed_path_set = {
                item for item in changed_paths if isinstance(item, str)
            }
            missing_test_paths = sorted(
                item
                for item in test_paths
                if isinstance(item, str) and item not in changed_path_set
            )
            if missing_test_paths:
                errors.append(
                    "$.generated_test_patch.test_paths: every test path must be "
                    "present in changed_paths"
                )

    integrity = instance.get("integrity_checks")
    if isinstance(patch, dict) and isinstance(integrity, dict):
        if integrity.get("checked_patch_sha256") != patch.get("patch_sha256"):
            errors.append(
                "$.integrity_checks.checked_patch_sha256: must match "
                "generated_test_patch.patch_sha256"
            )
        if integrity.get("checked_test_artifact_sha256") != patch.get(
            "test_artifact_sha256"
        ):
            errors.append(
                "$.integrity_checks.checked_test_artifact_sha256: must match "
                "generated_test_patch.test_artifact_sha256"
            )

    provenance = instance.get("generated_test_provenance")
    if isinstance(provenance, dict):
        if (
            instance.get("admission_decision") == "ADMIT"
            and provenance.get("provenance_status") != "COMPLETE"
        ):
            errors.append(
                "$.generated_test_provenance.provenance_status: ADMIT requires COMPLETE provenance"
            )
        if provenance.get("source_class") in {
            "SYNTHETIC_VERIFIED",
            "STUDENT_GENERATED",
            "TEACHER_GENERATED",
        }:
            generator_identity = provenance.get("generator_identity")
            if not isinstance(generator_identity, str) or not generator_identity:
                errors.append(
                    "$.generated_test_provenance.generator_identity: generated source classes "
                    "require generator identity"
                )
        if isinstance(patch, dict):
            artifact_sha = patch.get("test_artifact_sha256")
            lineage_identity = provenance.get("lineage_identity")
            expected_suffix = f"|test-artifact-sha256:{artifact_sha}"
            if (
                not isinstance(lineage_identity, str)
                or not lineage_identity.endswith(expected_suffix)
            ):
                errors.append(
                    "$.generated_test_provenance.lineage_identity: must bind the exact "
                    "generated_test_patch.test_artifact_sha256"
                )

    verifier_health = instance.get("verifier_health_binding")
    if isinstance(verifier_health, dict):
        if verifier_health.get("task_identity") != instance.get("task_identity"):
            errors.append(
                "$.verifier_health_binding.task_identity: must match task_identity"
            )
        if pre is not None and verifier_health.get("verifier_manifest_id") != pre.get(
            "verifier_manifest_id"
        ):
            errors.append(
                "$.verifier_health_binding.verifier_manifest_id: "
                "must match executed verifier manifest"
            )
        if post is not None and verifier_health.get("verifier_manifest_id") != post.get(
            "verifier_manifest_id"
        ):
            errors.append(
                "$.verifier_health_binding.verifier_manifest_id: "
                "must match executed verifier manifest"
            )

    behavior = instance.get("behavior_contract")
    if isinstance(behavior, dict):
        classes = behavior.get("test_classes")
        class_set = (
            {item for item in classes if isinstance(item, str)}
            if isinstance(classes, list)
            else set()
        )
        if behavior.get("requires_reproduction") is True and "REPRODUCTION" not in class_set:
            errors.append(
                "$.behavior_contract.test_classes: REPRODUCTION required when "
                "requires_reproduction=true"
            )
        if behavior.get("property_or_metamorphic_applicable") is True and not (
            {"PROPERTY", "METAMORPHIC"} & class_set
        ):
            errors.append(
                "$.behavior_contract.test_classes: PROPERTY or METAMORPHIC required "
                "when property_or_metamorphic_applicable=true"
            )

    mutation = instance.get("mutation_strength")
    if isinstance(mutation, dict):
        evaluated = mutation.get("mutants_evaluated")
        killed = mutation.get("mutants_killed")
        if (
            isinstance(evaluated, int)
            and not isinstance(evaluated, bool)
            and isinstance(killed, int)
            and not isinstance(killed, bool)
            and killed > evaluated
        ):
            errors.append("$.mutation_strength.mutants_killed: cannot exceed mutants_evaluated")
        if mutation.get("status") == "ADEQUATE":
            if not isinstance(mutation.get("evidence_identity"), str) or not mutation.get(
                "evidence_identity"
            ):
                errors.append(
                    "$.mutation_strength.evidence_identity: ADEQUATE requires concrete evidence"
                )
            if not isinstance(evaluated, int) or isinstance(evaluated, bool) or evaluated < 1:
                errors.append(
                    "$.mutation_strength.mutants_evaluated: ADEQUATE requires at least one mutant"
                )
            if not isinstance(killed, int) or isinstance(killed, bool) or killed < 1:
                errors.append(
                    "$.mutation_strength.mutants_killed: "
                    "ADEQUATE requires at least one killed mutant"
                )
        if mutation.get("status") == "NOT_APPLICABLE":
            justification = mutation.get("evidence_identity")
            if (
                not isinstance(justification, str)
                or not justification.startswith("not-applicable:")
                or not justification.removeprefix("not-applicable:").strip()
            ):
                errors.append(
                    "$.mutation_strength.evidence_identity: NOT_APPLICABLE requires "
                    "an explicit not-applicable:<justification> identity"
                )
            if evaluated != 0 or isinstance(evaluated, bool):
                errors.append(
                    "$.mutation_strength.mutants_evaluated: NOT_APPLICABLE requires "
                    "zero evaluated mutants"
                )
            if killed != 0 or isinstance(killed, bool):
                errors.append(
                    "$.mutation_strength.mutants_killed: NOT_APPLICABLE requires "
                    "zero killed mutants"
                )

    return tuple(sorted(errors))


def _trajectory_manifest_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce A017 identity bindings without implementing A018 admission execution."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    run_identity = instance.get("run_identity")
    verifier_health = instance.get("verifier_health_binding")
    if isinstance(run_identity, dict) and isinstance(verifier_health, dict):
        if verifier_health.get("task_identity") != run_identity.get("task_manifest_id"):
            errors.append(
                "$.verifier_health_binding.task_identity: must match run_identity.task_manifest_id"
            )
        if verifier_health.get("verifier_manifest_id") != run_identity.get(
            "verifier_manifest_id"
        ):
            errors.append(
                "$.verifier_health_binding.verifier_manifest_id: must match "
                "run_identity.verifier_manifest_id"
            )

    return tuple(sorted(errors))


def validation_errors(
    name: str,
    instance: Any,
    *,
    schema_dir: Path | None = None,
) -> tuple[str, ...]:
    """Return deterministic, human-readable validation errors."""

    schema = load_schema(name, schema_dir=schema_dir)
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            tuple(str(part) for part in error.absolute_schema_path),
            error.message,
        ),
    )
    formatted = [_format_validation_error(error) for error in errors]
    if name == "mstr-self-alignment-generation-v0":
        formatted.extend(_self_alignment_semantic_errors(instance))
    if name == "mstr-teacher-rescue-record-v0":
        formatted.extend(_teacher_rescue_semantic_errors(instance))
    if name == "mstr-difficulty-calibration-v0":
        formatted.extend(_difficulty_calibration_semantic_errors(instance))
    if name == "mstr-test-generation-example-v0":
        formatted.extend(_test_generation_semantic_errors(instance))
    if name == "mstr-trajectory-manifest-v0":
        formatted.extend(_trajectory_manifest_semantic_errors(instance))
    return tuple(sorted(formatted))


def validate_instance(
    name: str,
    instance: Any,
    *,
    schema_dir: Path | None = None,
) -> None:
    """Validate an already-decoded JSON value and fail closed on any violation."""

    errors = validation_errors(name, instance, schema_dir=schema_dir)
    if errors:
        joined = "\n".join(f"- {message}" for message in errors)
        raise SchemaValidationError(
            f"{name} validation failed:\n{joined}",
            code="schema.instance_invalid",
            details={"schema": name},
        )


def validate_json_file(
    name: str,
    path: Path,
    *,
    schema_dir: Path | None = None,
) -> None:
    """Load UTF-8 JSON from *path* and validate it against a registered schema."""

    try:
        instance = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SchemaValidationError(
            "unable to read JSON instance",
            code="schema.instance_read",
            details={"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(
            "instance is not valid JSON",
            code="schema.instance_json",
            details={"path": str(path), "reason": exc.msg},
        ) from exc
    validate_instance(name, instance, schema_dir=schema_dir)
