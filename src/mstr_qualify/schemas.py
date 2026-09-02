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
    # MSTR-000B B026: exact material-result identity and multi-fidelity research record.
    "mstr-material-result-identity-v0": "mstr-material-result-identity-v0.schema.json",
    "mstr-research-experiment-v2": "mstr-research-experiment-v2.schema.json",
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
        if proof.get("proof_kind") == "FAIL_BEFORE_PASS_AFTER" and instance.get(
            "base_revision"
        ) == instance.get("fix_revision"):
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
                errors.append("$.behavioral_proof: pre/post environment_identity must match")
            if pre.get("verifier_manifest_id") != post.get("verifier_manifest_id"):
                errors.append("$.behavioral_proof: pre/post verifier_manifest_id must match")
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
                execution_evidence_identities = {
                    value
                    for value in (
                        pre.get("evidence_identity"),
                        post.get("evidence_identity"),
                    )
                    if isinstance(value, str)
                }
                if (
                    evidence_identity is not None
                    and evidence_identity in execution_evidence_identities
                ):
                    errors.append(
                        "$.behavioral_proof.independent_acceptance_evidence_identity: "
                        "TASK_SPECIFIC_BEHAVIOR independent acceptance evidence must be "
                        "distinct from pre/post execution evidence identities"
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
            changed_path_set = {item for item in changed_paths if isinstance(item, str)}
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
        if integrity.get("checked_test_artifact_sha256") != patch.get("test_artifact_sha256"):
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
            if not isinstance(lineage_identity, str) or not lineage_identity.endswith(
                expected_suffix
            ):
                errors.append(
                    "$.generated_test_provenance.lineage_identity: must bind the exact "
                    "generated_test_patch.test_artifact_sha256"
                )

    verifier_health = instance.get("verifier_health_binding")
    if isinstance(verifier_health, dict):
        if verifier_health.get("task_identity") != instance.get("task_identity"):
            errors.append("$.verifier_health_binding.task_identity: must match task_identity")
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


_AMBIGUOUS_IDENTITY_SENTINELS = frozenset(
    {
        "unknown",
        "tbd",
        "unset",
        "none",
        "null",
        "na",
        "n/a",
        "?",
        "latest",
        "main",
        "master",
        "head",
    }
)
_B026_FIDELITY_LEVELS = (
    "L0_CONTRACT_SMOKE",
    "L1_CODE_PROXY",
    "L2_EXECUTABLE_REPO",
    "L3_DIRECTION_TO_DONE",
    "L4_Q4_UNIVERSAL_LAPTOP",
)
_B026_REQUIRED_GATE_IDS: Mapping[str, tuple[str, ...]] = {
    "L0_CONTRACT_SMOKE": (
        "contracts_config_valid",
        "l0_smoke_checks",
        "frozen_evaluation_pinned",
        "material_identity_complete",
        "authority_boundary_intact",
    ),
    "L1_CODE_PROXY": (
        "predecessor_promoted",
        "code_proxy_thresholds",
        "frozen_eval_tolerance",
        "material_identity_complete",
        "task_verifier_sampling_runtime_identity",
    ),
    "L2_EXECUTABLE_REPO": (
        "predecessor_promoted",
        "executable_repo_acceptance",
        "verifier_health",
        "shortcut_leakage_protection",
        "environment_runtime_task_verifier_identity",
    ),
    "L3_DIRECTION_TO_DONE": (
        "predecessor_promoted",
        "direction_to_done_acceptance",
        "hidden_acceptance_immutable",
        "product_regression_clear",
        "contract_harness_task_verifier_identity",
    ),
    "L4_Q4_UNIVERSAL_LAPTOP": (
        "predecessor_promoted",
        "q4_artifact_identity",
        "quantizer_runtime_hardware_identity",
        "universal_laptop_product_gates",
        "q4_promotion_record_promoted",
    ),
}
_B026_IDENTITY_OR_NA_FIELDS = (
    "model_id_or_na",
    "model_revision_or_na",
    "tokenizer_id_or_na",
    "tokenizer_revision_or_na",
    "quantization_method_or_na",
    "quantizer_tool_revision_or_na",
    "runtime_id_or_na",
    "runtime_version_or_commit_or_na",
    "runtime_build_flags_or_na",
    "os_identity_or_na",
    "cpu_identity_or_na",
    "acceleration_backend_or_na",
    "cache_state_or_na",
    "interaction_contract_version_or_na",
    "loop_contract_version_or_na",
    "harness_profile_id_or_na",
    "verifier_health_id_or_na",
    "sampling_config_id_or_na",
    "data_identity_or_na",
    "difficulty_identity_or_na",
    "invalidation_reason_or_na",
)


def _is_ambiguous_identity(value: object) -> bool:
    if not isinstance(value, str) or value == "N/A":
        return False
    return value != value.strip() or value.strip().casefold() in _AMBIGUOUS_IDENTITY_SENTINELS


def _material_result_identity_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Reject opaque B026 identity values that cannot support material comparison."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    for field in _B026_IDENTITY_OR_NA_FIELDS:
        value = instance.get(field)
        if _is_ambiguous_identity(value):
            errors.append(f"$.{field}: must be exact identity text or the literal 'N/A'")

    for field in ("task_manifest_id", "verifier_manifest_id"):
        value = instance.get(field)
        if _is_ambiguous_identity(value) or value == "N/A":
            errors.append(f"$.{field}: must be a concrete non-ambiguous identity")

    return tuple(sorted(errors))


_B026_GOVERNED_EFFECTS = (
    "MODEL_WEIGHT_ACCESS",
    "GATED_TERMS_ACCEPTANCE",
    "PAID_MODEL_API_EXECUTION",
    "PAID_COMPUTE",
    "RENTED_COMPUTE",
    "LARGE_DATASET_INGESTION",
    "WEIGHT_CHANGING_TRAINING",
    "LONG_TRAINING",
    "LARGE_SCALE_RL",
    "PRODUCTION_RELEASE",
)
_B026_LEVEL_CONCRETE_FIELDS: Mapping[str, tuple[str, ...]] = {
    "L1_CODE_PROXY": (
        "sampling_config_id_or_na",
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
    ),
    "L2_EXECUTABLE_REPO": (
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
        "os_identity_or_na",
        "cpu_identity_or_na",
        "verifier_health_id_or_na",
    ),
    "L3_DIRECTION_TO_DONE": (
        "interaction_contract_version_or_na",
        "loop_contract_version_or_na",
        "harness_profile_id_or_na",
        "verifier_health_id_or_na",
    ),
    "L4_Q4_UNIVERSAL_LAPTOP": (
        "model_id_or_na",
        "model_revision_or_na",
        "model_artifact_sha256_or_na",
        "tokenizer_id_or_na",
        "tokenizer_revision_or_na",
        "quantization_method_or_na",
        "quantizer_tool_revision_or_na",
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
        "runtime_build_flags_or_na",
        "os_identity_or_na",
        "cpu_identity_or_na",
        "acceleration_backend_or_na",
        "cache_state_or_na",
    ),
}


def _b026_binding_id(value: object) -> bool:
    """Return whether *value* can safely address a canonical binding file."""

    return bool(
        isinstance(value, str)
        and 1 <= len(value) <= 128
        and value[0].isalnum()
        and all(character.isalnum() or character in "._-" for character in value)
    )


def _b026_repository_json(
    repository_root: Path,
    relative_path: Path,
) -> tuple[dict[str, Any], str] | None:
    """Load one repository-contained non-symlink JSON record and its SHA-256."""

    root = repository_root.resolve()
    candidate = root / relative_path
    cursor = root
    for part in relative_path.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return None
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    if not resolved.is_file():
        return None
    try:
        raw = resolved.read_bytes()
        decoded = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(decoded, dict):
        return None
    return decoded, hashlib.sha256(raw).hexdigest()


def _b026_authority_limits(record: Mapping[str, Any]) -> dict[str, float]:
    """Derive research ceilings only from the canonical authority artifact."""

    ceiling = record.get("cost_resource_ceiling")
    if not isinstance(ceiling, dict):
        return {}
    limits = ceiling.get("limits")
    if not isinstance(limits, list):
        return {}
    derived: dict[str, float] = {}
    for item in limits:
        if not isinstance(item, dict):
            continue
        resource = item.get("resource")
        unit = item.get("unit")
        maximum = item.get("max")
        if (
            not isinstance(resource, str)
            or not isinstance(unit, str)
            or isinstance(maximum, bool)
            or not isinstance(maximum, (int, float))
            or not math.isfinite(float(maximum))
            or maximum < 0
        ):
            continue
        normalized_resource = resource.strip().casefold()
        normalized_unit = unit.strip().casefold()
        numeric = float(maximum)
        if normalized_resource in {"paid_cost_usd", "paid_cost", "cost"}:
            if normalized_unit == "usd":
                derived["max_paid_cost_usd"] = numeric
        elif normalized_resource in {"wall_time_seconds", "wall_time"}:
            multipliers = {
                "second": 1.0,
                "seconds": 1.0,
                "minute": 60.0,
                "minutes": 60.0,
                "hour": 3600.0,
                "hours": 3600.0,
            }
            multiplier = multipliers.get(normalized_unit)
            if multiplier is not None:
                derived["max_wall_time_seconds"] = numeric * multiplier
        elif normalized_resource in {
            "material_results",
            "material_result_count",
            "result_count",
        }:
            if normalized_unit in {"count", "result", "results"}:
                derived["max_material_results"] = numeric
    return derived


def _b026_true_effects(instance: Mapping[str, Any]) -> set[str]:
    """Return explicitly declared governed external effects."""

    declared = instance.get("governed_effects")
    if not isinstance(declared, dict):
        return set()
    return {effect for effect in _B026_GOVERNED_EFFECTS if declared.get(effect) is True}


def _b026_sha256_identity(value: Any) -> str | None:
    """Return the hex digest from one canonical sha256:<digest> identity."""

    if not isinstance(value, str) or not value.startswith("sha256:"):
        return None
    digest = value.removeprefix("sha256:")
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        return None
    return digest


def _b026_compare_gate_value(operator: Any, observed: Any, expected: Any) -> str | None:
    """Compute a gate status from one predeclared policy criterion."""

    if operator == "NOT_APPLICABLE":
        return "NOT_APPLICABLE" if observed is None else "FAIL"
    if operator == "EQ":
        return "PASS" if type(observed) is type(expected) and observed == expected else "FAIL"
    if operator in {"GTE", "LTE"}:
        if (
            isinstance(observed, bool)
            or isinstance(expected, bool)
            or not isinstance(observed, (int, float))
            or not isinstance(expected, (int, float))
            or not math.isfinite(float(observed))
            or not math.isfinite(float(expected))
        ):
            return None
        if operator == "GTE":
            return "PASS" if float(observed) >= float(expected) else "FAIL"
        return "PASS" if float(observed) <= float(expected) else "FAIL"
    return None


def _b026_promotion_policy_errors(
    instance: Mapping[str, Any],
    *,
    repository_root: Path,
) -> tuple[str, ...]:
    """Resolve predeclared policy and immutable gate evidence, then recompute statuses."""

    errors: list[str] = []
    task_id = instance.get("governing_task_id")
    level = instance.get("fidelity_level")
    campaign_id = instance.get("campaign_id")
    experiment_id = instance.get("experiment_id")
    evaluation_id = instance.get("frozen_evaluation_identity")
    policy_identity = instance.get("promotion_policy_identity")
    digest = _b026_sha256_identity(policy_identity)
    if not isinstance(task_id, str) or digest is None:
        return ("$.promotion_policy_identity: must bind a canonical predeclared policy",)

    policy_path = (
        Path("artifacts")
        / "results"
        / "research"
        / task_id
        / "promotion-policies"
        / f"{digest}.json"
    )
    loaded = _b026_repository_json(repository_root, policy_path)
    if loaded is None:
        return ("$.promotion_policy_identity: immutable predeclared policy record missing",)
    policy, observed_sha = loaded
    if observed_sha != digest:
        errors.append("$.promotion_policy_identity: policy content address mismatch")

    expected_policy_keys = {
        "schema_version",
        "governing_task_id",
        "campaign_id",
        "fidelity_level",
        "frozen_evaluation_identity",
        "criteria",
    }
    if set(policy) != expected_policy_keys:
        errors.append("$.promotion_policy_identity: policy record fields are not canonical")
    if policy.get("schema_version") != "mstr.research-promotion-policy.v0":
        errors.append("$.promotion_policy_identity: unsupported policy schema_version")
    for field, expected_policy_value in (
        ("governing_task_id", task_id),
        ("campaign_id", campaign_id),
        ("fidelity_level", level),
        ("frozen_evaluation_identity", evaluation_id),
    ):
        if policy.get(field) != expected_policy_value:
            errors.append(f"$.promotion_policy_identity: policy {field} must match experiment")

    criteria_raw = policy.get("criteria")
    criteria: dict[str, dict[str, Any]] = {}
    if not isinstance(criteria_raw, list):
        errors.append("$.promotion_policy_identity: policy criteria must be an array")
    else:
        for criterion in criteria_raw:
            if not isinstance(criterion, dict) or set(criterion) != {
                "gate_id",
                "operator",
                "expected_value",
            }:
                errors.append("$.promotion_policy_identity: malformed policy criterion")
                continue
            gate_id = criterion.get("gate_id")
            if not isinstance(gate_id, str) or gate_id in criteria:
                errors.append("$.promotion_policy_identity: duplicate or invalid policy gate_id")
                continue
            if criterion.get("operator") not in {
                "EQ",
                "GTE",
                "LTE",
                "NOT_APPLICABLE",
                "EQ_PROMOTED_ARTIFACT",
            }:
                errors.append("$.promotion_policy_identity: unsupported policy operator")
                continue
            criteria[gate_id] = criterion

    if isinstance(level, str) and level in _B026_REQUIRED_GATE_IDS:
        required = _B026_REQUIRED_GATE_IDS[level]
        if set(criteria) != set(required) or len(criteria) != len(required):
            errors.append(
                "$.promotion_policy_identity: policy must exactly cover required gate ids"
            )

    gates = instance.get("hard_gate_results")
    if not isinstance(gates, list):
        return tuple(sorted(errors))
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            continue
        gate_id = gate.get("gate_id")
        criterion = criteria.get(gate_id) if isinstance(gate_id, str) else None
        if criterion is None:
            errors.append(f"$.hard_gate_results[{index}]: no predeclared criterion for gate")
            continue
        evidence_identity = gate.get("evidence_identity")
        evidence_digest = _b026_sha256_identity(evidence_identity)
        if evidence_digest is None:
            errors.append(
                f"$.hard_gate_results[{index}].evidence_identity: must be sha256 content address"
            )
            continue
        evidence_path = (
            Path("artifacts")
            / "results"
            / "research"
            / task_id
            / "gate-evidence"
            / f"{evidence_digest}.json"
        )
        loaded_evidence = _b026_repository_json(repository_root, evidence_path)
        if loaded_evidence is None:
            errors.append(
                f"$.hard_gate_results[{index}].evidence_identity: canonical evidence missing"
            )
            continue
        evidence_record, evidence_sha = loaded_evidence
        if evidence_sha != evidence_digest:
            errors.append(
                f"$.hard_gate_results[{index}].evidence_identity: evidence content address mismatch"
            )
        expected_evidence_keys = {
            "schema_version",
            "governing_task_id",
            "campaign_id",
            "experiment_id",
            "gate_id",
            "observed_value",
        }
        if set(evidence_record) != expected_evidence_keys:
            errors.append(f"$.hard_gate_results[{index}]: gate evidence fields are not canonical")
        if evidence_record.get("schema_version") != "mstr.research-gate-evidence.v0":
            errors.append(f"$.hard_gate_results[{index}]: unsupported gate evidence schema_version")
        for field, expected_evidence_value in (
            ("governing_task_id", task_id),
            ("campaign_id", campaign_id),
            ("experiment_id", experiment_id),
            ("gate_id", gate_id),
        ):
            if evidence_record.get(field) != expected_evidence_value:
                errors.append(
                    f"$.hard_gate_results[{index}]: gate evidence {field} must match experiment"
                )
        operator = criterion.get("operator")
        computed: str | None
        if operator == "EQ_PROMOTED_ARTIFACT":
            promoted_id = instance.get("promoted_result_id_or_na")
            material_results = instance.get("material_results")
            promoted_artifact: Any = None
            if isinstance(promoted_id, str) and isinstance(material_results, list):
                for result in material_results:
                    if isinstance(result, dict) and result.get("result_id") == promoted_id:
                        promoted_artifact = result.get("model_artifact_sha256_or_na")
                        break
            computed = (
                "PASS"
                if isinstance(promoted_artifact, str)
                and promoted_artifact != "N/A"
                and evidence_record.get("observed_value") == promoted_artifact
                else "FAIL"
            )
        else:
            computed = _b026_compare_gate_value(
                operator,
                evidence_record.get("observed_value"),
                criterion.get("expected_value"),
            )
        if computed is None:
            errors.append(f"$.hard_gate_results[{index}]: policy criterion cannot be evaluated")
        elif gate.get("status") != computed:
            errors.append(
                f"$.hard_gate_results[{index}].status: submitted status does not match "
                "predeclared criterion"
            )
    return tuple(sorted(errors))


def _research_experiment_semantic_errors(
    instance: Any,
    *,
    repository_root: Path,
    schema_dir: Path | None = None,
    visited_records: frozenset[str] = frozenset(),
) -> tuple[str, ...]:
    """Enforce B026 lineage, material identity, budgets, and canonical authority."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    level = instance.get("fidelity_level")
    governing_task_id = instance.get("governing_task_id")
    predecessor = instance.get("predecessor_promotion")
    promotion_decision = instance.get("promotion_decision")

    material_results = instance.get("material_results")
    result_by_id: dict[str, dict[str, Any]] = {}
    paid_result_total = 0.0
    paid_result_total_valid = True
    if isinstance(material_results, list):
        result_ids: list[str] = []
        for index, result in enumerate(material_results):
            if not isinstance(result, dict):
                continue
            result_id = result.get("result_id")
            if isinstance(result_id, str):
                result_ids.append(result_id)
                result_by_id[result_id] = result
            paid = result.get("paid_cost_usd")
            if isinstance(paid, (int, float)) and not isinstance(paid, bool):
                paid_result_total += float(paid)
            else:
                paid_result_total_valid = False
            for message in _material_result_identity_semantic_errors(result):
                suffix = message[1:] if message.startswith("$") else f".{message}"
                errors.append(f"$.material_results[{index}]{suffix}")
        if len(result_ids) != len(set(result_ids)):
            errors.append("$.material_results: result_id values must be unique")

    promoted_result_id = instance.get("promoted_result_id_or_na")
    promoted_result: dict[str, Any] | None = None
    if promotion_decision == "PROMOTE":
        if not isinstance(promoted_result_id, str) or promoted_result_id == "N/A":
            errors.append("$.promoted_result_id_or_na: PROMOTE requires one concrete result_id")
        else:
            promoted_result = result_by_id.get(promoted_result_id)
            if promoted_result is None:
                errors.append(
                    "$.promoted_result_id_or_na: must resolve to one material_results result_id"
                )
            elif promoted_result.get("result_classification") not in {"PASS", "PROMOTED"}:
                errors.append(
                    "$.promoted_result_id_or_na: promoted material result must be PASS or PROMOTED"
                )
    elif promoted_result_id != "N/A":
        errors.append("$.promoted_result_id_or_na: non-PROMOTE decisions require literal N/A")

    if level == _B026_FIDELITY_LEVELS[0]:
        if predecessor is not None:
            errors.append("$.predecessor_promotion: L0 must not claim a predecessor promotion")
    elif level in _B026_FIDELITY_LEVELS[1:]:
        expected_level = _B026_FIDELITY_LEVELS[_B026_FIDELITY_LEVELS.index(level) - 1]
        if not isinstance(predecessor, dict):
            errors.append(
                "$.predecessor_promotion: L1-L4 require immutable predecessor registry evidence"
            )
        else:
            predecessor_id = predecessor.get("experiment_id")
            predecessor_sha = predecessor.get("experiment_record_sha256")
            if not _b026_binding_id(predecessor_id):
                errors.append(
                    "$.predecessor_promotion.experiment_id: must be a path-safe stable binding id"
                )
            elif not isinstance(governing_task_id, str):
                errors.append("$.governing_task_id: required to resolve predecessor registry")
            else:
                relative = (
                    Path("artifacts")
                    / "results"
                    / "research"
                    / governing_task_id
                    / "registry"
                    / f"{predecessor_id}.json"
                )
                registry_key = relative.as_posix()
                if registry_key in visited_records:
                    errors.append("$.predecessor_promotion: predecessor registry cycle detected")
                else:
                    loaded = _b026_repository_json(repository_root, relative)
                    if loaded is None:
                        errors.append(
                            "$.predecessor_promotion: immutable predecessor registry record missing"
                        )
                    else:
                        predecessor_record, observed_sha = loaded
                        if predecessor_sha != observed_sha:
                            errors.append(
                                "$.predecessor_promotion.experiment_record_sha256: "
                                "does not match immutable predecessor record"
                            )
                        nested_errors = validation_errors(
                            "mstr-research-experiment-v2",
                            predecessor_record,
                            schema_dir=schema_dir,
                            repository_root=repository_root,
                            _research_visited=visited_records | {registry_key},
                        )
                        if nested_errors:
                            errors.append(
                                "$.predecessor_promotion: referenced predecessor record is invalid"
                            )
                        if predecessor_record.get("experiment_id") != predecessor_id:
                            errors.append(
                                "$.predecessor_promotion.experiment_id: registry record "
                                "identity mismatch"
                            )
                        if predecessor_record.get("governing_task_id") != governing_task_id:
                            errors.append(
                                "$.predecessor_promotion: predecessor governing task must match"
                            )
                        if predecessor_record.get("campaign_id") != instance.get("campaign_id"):
                            errors.append(
                                "$.predecessor_promotion: predecessor campaign_id must match"
                            )
                        if predecessor_record.get("fidelity_level") != expected_level:
                            errors.append(
                                "$.predecessor_promotion: registry record must be immediate "
                                "predecessor level"
                            )
                        if predecessor_record.get("promotion_decision") != "PROMOTE":
                            errors.append(
                                "$.predecessor_promotion: registry predecessor must have "
                                "PROMOTE decision"
                            )
                        if predecessor_record.get("frozen_evaluation_identity") != instance.get(
                            "frozen_evaluation_identity"
                        ):
                            errors.append(
                                "$.predecessor_promotion: frozen evaluation identity must match"
                            )
                        predecessor_result = predecessor_record.get("promoted_result_id_or_na")
                        if predecessor_result == "N/A" or predecessor_result != instance.get(
                            "parent_identity"
                        ):
                            errors.append(
                                "$.parent_identity: must equal registry predecessor promoted result"
                            )

    errors.extend(_b026_promotion_policy_errors(instance, repository_root=repository_root))

    hard_gates = instance.get("hard_gate_results")
    gate_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(hard_gates, list):
        gate_ids = [
            gate.get("gate_id")
            for gate in hard_gates
            if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str)
        ]
        for gate in hard_gates:
            if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str):
                gate_by_id[str(gate["gate_id"])] = gate
        if len(gate_ids) != len(set(gate_ids)):
            errors.append("$.hard_gate_results: gate_id values must be unique")
        if (
            promotion_decision == "PROMOTE"
            and isinstance(level, str)
            and level in _B026_REQUIRED_GATE_IDS
        ):
            expected_gate_ids = _B026_REQUIRED_GATE_IDS[level]
            if set(gate_ids) != set(expected_gate_ids) or len(gate_ids) != len(expected_gate_ids):
                errors.append(
                    "$.hard_gate_results: PROMOTE requires exact per-level required gate coverage"
                )

    if promotion_decision == "PROMOTE" and isinstance(level, str) and promoted_result is not None:
        for field in _B026_LEVEL_CONCRETE_FIELDS.get(level, ()):
            value = promoted_result.get(field)
            if value == "N/A" or value is None:
                errors.append(
                    f"$.material_results[{promoted_result_id}].{field}: "
                    f"{level} promotion requires concrete identity"
                )
        if level == "L4_Q4_UNIVERSAL_LAPTOP":
            for field in (
                "total_ram_bytes_or_na",
                "thread_count_or_na",
                "context_length_or_na",
            ):
                value = promoted_result.get(field)
                if isinstance(value, bool) or not isinstance(value, int):
                    errors.append(
                        f"$.material_results[{promoted_result_id}].{field}: "
                        "L4 promotion requires a concrete integer identity"
                    )
            q4_record_identity = instance.get("q4_promotion_record_identity_or_na")
            q4_digest = _b026_sha256_identity(q4_record_identity)
            artifact_sha = promoted_result.get("model_artifact_sha256_or_na")
            if q4_digest is None:
                errors.append(
                    "$.q4_promotion_record_identity_or_na: L4 PROMOTE requires a "
                    "sha256-bound Q4 record"
                )
            else:
                q4_path = (
                    Path("artifacts")
                    / "results"
                    / "q4-promotion"
                    / "registry"
                    / f"{q4_digest}.json"
                )
                loaded_q4 = _b026_repository_json(repository_root, q4_path)
                if loaded_q4 is None:
                    errors.append(
                        "$.q4_promotion_record_identity_or_na: immutable Q4 promotion "
                        "record missing"
                    )
                else:
                    q4_record, observed_q4_sha = loaded_q4
                    if observed_q4_sha != q4_digest:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: Q4 record content address "
                            "mismatch"
                        )
                    q4_errors = validation_errors(
                        "mstr-q4-promotion-v0",
                        q4_record,
                        schema_dir=schema_dir,
                        repository_root=repository_root,
                    )
                    if q4_errors:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: referenced Q4 promotion record "
                            "is invalid"
                        )
                    if q4_record.get("promotion_status") != "PROMOTED":
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: referenced Q4 record must be "
                            "PROMOTED"
                        )
                    if q4_record.get("canonical_q4_artifact_sha256") != artifact_sha:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: Q4 record artifact must match "
                            "promoted result"
                        )
                    if q4_record.get("universal_laptop_gate_result") != "PASS":
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: L4 requires universal-laptop "
                            "gate PASS"
                        )
                    laptop_gate = gate_by_id.get("universal_laptop_product_gates")
                    if isinstance(laptop_gate, dict) and q4_record.get(
                        "universal_laptop_gate_evidence_identity"
                    ) != laptop_gate.get("evidence_identity"):
                        errors.append(
                            "$.hard_gate_results[universal_laptop_product_gates]."
                            "evidence_identity: "
                            "must match resolved Q4 universal-laptop evidence"
                        )
                    promotion_gate = gate_by_id.get("q4_promotion_record_promoted")
                    if isinstance(promotion_gate, dict) and q4_record.get(
                        "promotion_decision_evidence_identity"
                    ) != promotion_gate.get("evidence_identity"):
                        errors.append(
                            "$.hard_gate_results[q4_promotion_record_promoted].evidence_identity: "
                            "must match resolved Q4 promotion-decision evidence"
                        )
    if (
        not (
            promotion_decision == "PROMOTE"
            and level == "L4_Q4_UNIVERSAL_LAPTOP"
            and promoted_result is not None
        )
        and instance.get("q4_promotion_record_identity_or_na") != "N/A"
    ):
        errors.append(
            "$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence"
        )

    budget = instance.get("budget")
    aggregate = instance.get("aggregate_resource_cost")
    if isinstance(material_results, list) and isinstance(budget, dict):
        maximum = budget.get("max_material_results")
        if (
            isinstance(maximum, int)
            and not isinstance(maximum, bool)
            and len(material_results) > maximum
        ):
            errors.append("$.material_results: count exceeds budget.max_material_results")

    if isinstance(material_results, list) and isinstance(aggregate, dict):
        count = aggregate.get("material_result_count")
        if (
            isinstance(count, int)
            and not isinstance(count, bool)
            and count != len(material_results)
        ):
            errors.append(
                "$.aggregate_resource_cost.material_result_count: must equal "
                "material_results length"
            )
        aggregate_paid = aggregate.get("paid_cost_usd")
        if (
            paid_result_total_valid
            and isinstance(aggregate_paid, (int, float))
            and not isinstance(aggregate_paid, bool)
            and not math.isclose(
                paid_result_total,
                float(aggregate_paid),
                rel_tol=0.0,
                abs_tol=1e-9,
            )
        ):
            errors.append(
                "$.aggregate_resource_cost.paid_cost_usd: "
                "must equal sum(material_results[*].paid_cost_usd)"
            )

    if isinstance(budget, dict) and isinstance(aggregate, dict):
        wall = aggregate.get("wall_time_seconds")
        max_wall = budget.get("max_wall_time_seconds")
        if (
            isinstance(wall, (int, float))
            and not isinstance(wall, bool)
            and isinstance(max_wall, (int, float))
            and not isinstance(max_wall, bool)
            and wall > max_wall
        ):
            errors.append(
                "$.aggregate_resource_cost.wall_time_seconds: exceeds budget.max_wall_time_seconds"
            )
        paid = aggregate.get("paid_cost_usd")
        max_paid = budget.get("max_paid_cost_usd")
        if (
            isinstance(paid, (int, float))
            and not isinstance(paid, bool)
            and isinstance(max_paid, (int, float))
            and not isinstance(max_paid, bool)
            and paid > max_paid
        ):
            errors.append(
                "$.aggregate_resource_cost.paid_cost_usd: exceeds budget.max_paid_cost_usd"
            )
        budget_class = budget.get("resource_class")
        aggregate_class = aggregate.get("resource_class")
        if budget_class == "CONTRACT_ONLY" and aggregate_class != "CONTRACT_ONLY":
            errors.append(
                "$.aggregate_resource_cost.resource_class: "
                "CONTRACT_ONLY budget requires CONTRACT_ONLY aggregate"
            )
        if budget_class == "LOCAL_BOUNDED" and aggregate_class == "AUTHORIZED_EXTERNAL_EFFECT":
            errors.append(
                "$.aggregate_resource_cost.resource_class: "
                "LOCAL_BOUNDED budget cannot record authorized external effect"
            )

    declared_effects = _b026_true_effects(instance)
    if isinstance(material_results, list):
        for result in material_results:
            if not isinstance(result, dict):
                continue
            if (
                result.get("evidence_kind") == "TRAINING_EVIDENCE"
                and "WEIGHT_CHANGING_TRAINING" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.WEIGHT_CHANGING_TRAINING: "
                    "TRAINING_EVIDENCE requires explicit true declaration"
                )
            resource_cost = result.get("resource_cost")
            if isinstance(resource_cost, dict) and (
                resource_cost.get("cost_class") == "AUTHORIZED_REMOTE_COMPUTE"
                and "RENTED_COMPUTE" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.RENTED_COMPUTE: "
                    "AUTHORIZED_REMOTE_COMPUTE requires explicit true declaration"
                )
            paid = result.get("paid_cost_usd")
            if (
                isinstance(paid, (int, float))
                and not isinstance(paid, bool)
                and paid > 0
                and "PAID_COMPUTE" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.PAID_COMPUTE: positive paid cost requires "
                    "explicit true declaration"
                )

    external_resource_class = bool(
        isinstance(budget, dict)
        and budget.get("resource_class") == "EXTERNAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY"
    ) or bool(
        isinstance(aggregate, dict)
        and aggregate.get("resource_class") == "AUTHORIZED_EXTERNAL_EFFECT"
    )
    if external_resource_class and not declared_effects:
        errors.append(
            "$.governed_effects: external-effect resource class requires at least "
            "one true governed effect"
        )

    authority = instance.get("external_effect_authority")
    if declared_effects:
        if not isinstance(authority, dict):
            errors.append("$.external_effect_authority: required when any governed effect is true")
        else:
            authority_id = authority.get("authority_id")
            authority_sha = authority.get("authority_record_sha256")
            if not _b026_binding_id(authority_id):
                errors.append(
                    "$.external_effect_authority.authority_id: must be a path-safe "
                    "canonical binding id"
                )
            else:
                relative = Path("artifacts") / "authorities" / f"{authority_id}.json"
                loaded = _b026_repository_json(repository_root, relative)
                if loaded is None:
                    errors.append(
                        "$.external_effect_authority: canonical authority record missing or invalid"
                    )
                else:
                    authority_record, observed_sha = loaded
                    if authority_sha != observed_sha:
                        errors.append(
                            "$.external_effect_authority.authority_record_sha256: "
                            "does not match canonical authority record"
                        )
                    if authority_record.get("authority_id") != authority_id:
                        errors.append(
                            "$.external_effect_authority.authority_id: canonical record "
                            "identity mismatch"
                        )
                    if authority_record.get("status") != "AUTHORIZED_CANONICAL":
                        errors.append(
                            "$.external_effect_authority: canonical authority status must "
                            "be AUTHORIZED_CANONICAL"
                        )
                    if authority_record.get("task_id") != governing_task_id:
                        errors.append(
                            "$.external_effect_authority: canonical authority task_id must "
                            "match governing_task_id"
                        )
                    if authority_record.get("external_effect_class") not in declared_effects:
                        errors.append(
                            "$.external_effect_authority: canonical strongest effect must "
                            "be declared true"
                        )
                    scope = authority_record.get("scope")
                    if not isinstance(scope, dict):
                        errors.append(
                            "$.external_effect_authority: canonical authority scope is invalid"
                        )
                    else:
                        if scope.get("campaign_id") != instance.get("campaign_id"):
                            errors.append(
                                "$.external_effect_authority: canonical authority campaign "
                                "scope mismatch"
                            )
                        if scope.get("research_ladder_id") != "mstr-research-ladder-v0":
                            errors.append(
                                "$.external_effect_authority: canonical authority ladder "
                                "scope mismatch"
                            )
                        research_effects = scope.get("research_effects")
                        if not isinstance(research_effects, list) or not declared_effects.issubset(
                            set(research_effects)
                        ):
                            errors.append(
                                "$.external_effect_authority: canonical authority scope misses "
                                "declared effect"
                            )
                    ceilings = _b026_authority_limits(authority_record)
                    required_ceilings = {
                        "max_paid_cost_usd",
                        "max_wall_time_seconds",
                        "max_material_results",
                    }
                    if not required_ceilings.issubset(ceilings):
                        errors.append(
                            "$.external_effect_authority: canonical authority lacks research "
                            "resource ceilings"
                        )
                    else:
                        if isinstance(budget, dict):
                            for field in sorted(required_ceilings):
                                declared = budget.get(field)
                                if (
                                    isinstance(declared, (int, float))
                                    and not isinstance(declared, bool)
                                    and float(declared) > ceilings[field]
                                ):
                                    errors.append(
                                        f"$.budget.{field}: exceeds resolved canonical "
                                        "authority ceiling"
                                    )
                        if isinstance(aggregate, dict):
                            for field in sorted(required_ceilings):
                                aggregate_field = (
                                    "paid_cost_usd"
                                    if field == "max_paid_cost_usd"
                                    else "wall_time_seconds"
                                    if field == "max_wall_time_seconds"
                                    else "material_result_count"
                                )
                                actual = aggregate.get(aggregate_field)
                                if (
                                    isinstance(actual, (int, float))
                                    and not isinstance(actual, bool)
                                    and float(actual) > ceilings[field]
                                ):
                                    errors.append(
                                        f"$.aggregate_resource_cost.{aggregate_field}: "
                                        "exceeds resolved canonical authority ceiling"
                                    )
    elif authority is not None:
        errors.append(
            "$.external_effect_authority: must be null when all governed effects are false"
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
        if verifier_health.get("verifier_manifest_id") != run_identity.get("verifier_manifest_id"):
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
    repository_root: Path | None = None,
    _research_visited: frozenset[str] | None = None,
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
    if name == "mstr-material-result-identity-v0":
        formatted.extend(_material_result_identity_semantic_errors(instance))
    if name == "mstr-research-experiment-v2":
        formatted.extend(
            _research_experiment_semantic_errors(
                instance,
                repository_root=(repository_root or _REPOSITORY_ROOT).resolve(),
                schema_dir=schema_dir,
                visited_records=_research_visited or frozenset(),
            )
        )
    if name == "mstr-trajectory-manifest-v0":
        formatted.extend(_trajectory_manifest_semantic_errors(instance))
    return tuple(sorted(formatted))


def validate_instance(
    name: str,
    instance: Any,
    *,
    schema_dir: Path | None = None,
    repository_root: Path | None = None,
) -> None:
    """Validate an already-decoded JSON value and fail closed on any violation."""

    errors = validation_errors(
        name,
        instance,
        schema_dir=schema_dir,
        repository_root=repository_root,
    )
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
