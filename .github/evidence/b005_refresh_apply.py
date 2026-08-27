from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

EXPECTED_MAIN = os.environ.get("EXPECTED_MAIN", "").strip()
ENTRY_GATE_RUN = "33103275261"
ENTRY_GATE_JOB = "98626338825"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
HF_API = "https://huggingface.co/api/models/"
USER_AGENT = "MSTR-B005-public-metadata-refresh/1.0"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_compact_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")


def _git_blob(root: Path, path: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip().lower()
    if not SHA40.fullmatch(value):
        raise SystemExit(f"invalid Git blob identity for {path}: {value!r}")
    return value


def _hf_model(repo_id: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(repo_id, safe="/")
    request = urllib.request.Request(
        HF_API + encoded,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        method="GET",
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status != 200:
                    raise RuntimeError(f"unexpected status {response.status} for {repo_id}")
                payload = json.loads(response.read().decode("utf-8"))
            sha = str(payload.get("sha", "")).lower()
            if not SHA40.fullmatch(sha):
                raise RuntimeError(f"missing exact current SHA for {repo_id}: {sha!r}")
            return payload
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    raise SystemExit(f"public metadata lookup failed for {repo_id}: {last_error}")


def _license_tag(payload: dict[str, Any]) -> str:
    card = payload.get("cardData")
    if isinstance(card, dict):
        value = card.get("license")
        if isinstance(value, str) and value.strip():
            return value.strip()
    for tag in payload.get("tags", []) if isinstance(payload.get("tags"), list) else []:
        if isinstance(tag, str) and tag.startswith("license:"):
            return tag.split(":", 1)[1]
    return "UNRESOLVED_PUBLIC_METADATA"


def _gated_value(payload: dict[str, Any]) -> str:
    value = payload.get("gated")
    if value is True:
        return "true"
    if value is False or value is None:
        return "false"
    return str(value)


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _exact_tree_url(repo_id: str, sha: str) -> str:
    return f"https://huggingface.co/{repo_id}/tree/{sha}"


def _new_record(
    *,
    repo_id: str,
    payload: dict[str, Any],
    specialization: str,
    provenance: str,
    license_observation: str,
    access_observation: str,
    parameter_observation: str,
    context_tokens: int,
    intended_use: str,
    flags: list[str],
) -> dict[str, Any]:
    sha = str(payload["sha"]).lower()
    if not SHA40.fullmatch(sha):
        raise SystemExit(f"new record lacks exact SHA: {repo_id}")
    return {
        "repo_id": repo_id,
        "current_revision": sha,
        "revision_status": "EXACT_FULL_SHA",
        "existing_candidate_id": None,
        "specialization": specialization,
        "provenance_observation": provenance,
        "license_observation": license_observation,
        "access_gate_observation": access_observation,
        "parameter_observation": parameter_observation,
        "context_observation_tokens": context_tokens,
        "intended_use_observation": intended_use,
        "material_flags": flags,
        "source_urls": [
            f"https://huggingface.co/{repo_id}",
            _exact_tree_url(repo_id, sha),
        ],
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: b005_refresh_apply.py <repo-root>")
    if not SHA40.fullmatch(EXPECTED_MAIN):
        raise SystemExit("EXPECTED_MAIN must be an exact 40-hex canonical commit")

    root = Path(sys.argv[1]).resolve()
    discovery_path = root / "artifacts/manifests/B005-code-backbone-discovery.json"
    binding_path = root / "artifacts/manifests/B005-canonical-input-binding.json"
    evidence_path = root / "evidence/mstr-000b/B005-code-backbone-rescan.md"
    validation_path = root / "evidence/mstr-000b/B005-schema-validation.md"

    discovery = _read_json(discovery_path)
    if discovery.get("task_id") != "B005":
        raise SystemExit("unexpected discovery task identity")
    if discovery.get("no_weight_access_performed") is not True or discovery.get("no_authority_created") is not True:
        raise SystemExit("B005 discovery authority invariants are not fail-closed")
    scope = discovery.get("scope")
    if not isinstance(scope, dict) or scope.get("model_weight_access") is not False:
        raise SystemExit("B005 discovery scope would allow model weight access")

    candidates = discovery.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise SystemExit("B005 candidates missing")
    repo_ids = [entry.get("repo_id") for entry in candidates if isinstance(entry, dict)]
    if len(repo_ids) != len(set(repo_ids)):
        raise SystemExit("duplicate repo_id in existing B005 discovery")

    # Public Hugging Face model API metadata only. No resolve/download endpoints,
    # tokenizer files, model files, gated-term acceptance, or inference are used.
    metadata: dict[str, dict[str, Any]] = {}
    refresh_rows: list[tuple[str, str | None, str, str, str]] = []
    for entry in candidates:
        if not isinstance(entry, dict):
            raise SystemExit("non-object B005 candidate")
        repo_id = str(entry["repo_id"])
        payload = _hf_model(repo_id)
        metadata[repo_id] = payload
        new_sha = str(payload["sha"]).lower()
        old_sha = entry.get("current_revision") if isinstance(entry.get("current_revision"), str) else None
        if old_sha != new_sha:
            _append_unique(entry["material_flags"], "REVISION_DRIFT_SINCE_INITIAL_B005")
        entry["current_revision"] = new_sha
        entry["revision_status"] = "EXACT_FULL_SHA"
        _append_unique(entry["source_urls"], _exact_tree_url(repo_id, new_sha))
        refresh_rows.append((repo_id, old_sha, new_sha, _license_tag(payload), _gated_value(payload)))

    required_new = [
        "LiquidAI/LFM2.5-1.2B-Base",
        "Qwen/Qwen3.5-0.8B-Base",
        "zai-org/GLM-5.3-Flash",
        "moonshotai/Kimi-K2-Base",
    ]
    for repo_id in required_new:
        if repo_id in repo_ids:
            raise SystemExit(f"refresh record unexpectedly already present: {repo_id}")
        metadata[repo_id] = _hf_model(repo_id)

    lfm = metadata["LiquidAI/LFM2.5-1.2B-Base"]
    candidates.append(
        _new_record(
            repo_id="LiquidAI/LFM2.5-1.2B-Base",
            payload=lfm,
            specialization="general_base_hybrid_on_device",
            provenance="Current public model card identifies a pre-trained text-only base checkpoint used to create the LFM2.5 1.2B variants.",
            license_observation="other / Liquid model license metadata; exact derivative redistribution and accountless-release rights require B006 review.",
            access_observation="NO_PUBLIC_GATE_OBSERVED",
            parameter_observation="1.17B total parameters; 1.2B family label.",
            context_tokens=32768,
            intended_use="On-device-oriented pre-trained base for fine-tuning; official metadata also describes Transformers/vLLM and GGUF/ONNX deployment paths.",
            flags=[
                "NEWLY_RELEVANT",
                "B006_REVIEW_REQUIRED",
                "B006_RIGHTS_REVIEW_REQUIRED",
                "ON_DEVICE_RELEVANT",
                "LOW_PARAMETER_CANDIDATE_OR_CONTROL",
                "B009_RUNTIME_COMPATIBILITY_REVIEW_REQUIRED",
            ],
        )
    )

    qwen = metadata["Qwen/Qwen3.5-0.8B-Base"]
    candidates.append(
        _new_record(
            repo_id="Qwen/Qwen3.5-0.8B-Base",
            payload=qwen,
            specialization="general_base_multimodal_lower_bound",
            provenance="Repository describes a pre-trained-only model, while the current card also labels Training Stage as Pre-training & Post-training; B006 must reconcile this provenance before primary admission.",
            license_observation="apache-2.0",
            access_observation="NO_PUBLIC_GATE_OBSERVED",
            parameter_observation="0.8B language-model parameters; Hugging Face model-size metadata is approximately 0.9B and a vision encoder is present.",
            context_tokens=262144,
            intended_use="Compact lower-bound/base control for fine-tuning and development experiments; multimodal component cost must remain separate from the universal-laptop language-model comparison.",
            flags=[
                "NEWLY_RELEVANT",
                "B006_REVIEW_REQUIRED",
                "LOWER_BOUND_CONTROL_OR_CANDIDATE",
                "PROVENANCE_REVALIDATION_REQUIRED",
                "VISION_COMPONENT_COST_REVIEW",
            ],
        )
    )

    glm = metadata["zai-org/GLM-5.3-Flash"]
    candidates.append(
        _new_record(
            repo_id="zai-org/GLM-5.3-Flash",
            payload=glm,
            specialization="frontier_reference_screened_out_scale",
            provenance="Released Flash checkpoint is a frontier multimodal/agentic model; B005 does not establish it as a clean compact foundation and screens it before B006 qualification because it violates the primary product scale envelope.",
            license_observation="mit",
            access_observation="NO_PUBLIC_GATE_OBSERVED",
            parameter_observation="320B total parameters / 18B active parameters.",
            context_tokens=1048576,
            intended_use="Frontier coding/agentic reference only; not a universal-laptop primary-backbone qualification candidate.",
            flags=[
                "FRONTIER_REFERENCE_ONLY",
                "SCREENED_OUT_PRODUCT_SCALE",
                "NOT_B006_QUALIFICATION_CANDIDATE",
                "PROVENANCE_NOT_ESTABLISHED_AS_COMPACT_BASE",
            ],
        )
    )

    kimi = metadata["moonshotai/Kimi-K2-Base"]
    candidates.append(
        _new_record(
            repo_id="moonshotai/Kimi-K2-Base",
            payload=kimi,
            specialization="frontier_reference_screened_out_scale",
            provenance="Public model card explicitly identifies Kimi-K2-Base as the foundation checkpoint, but its MoE scale is incompatible with the MSTR universal-laptop primary product.",
            license_observation="modified-mit",
            access_observation="NO_PUBLIC_GATE_OBSERVED",
            parameter_observation="1T total parameters / 32B active parameters.",
            context_tokens=131072,
            intended_use="Frontier coding/agentic base reference only; not a universal-laptop primary-backbone qualification candidate.",
            flags=[
                "FRONTIER_REFERENCE_ONLY",
                "SCREENED_OUT_PRODUCT_SCALE",
                "NOT_B006_QUALIFICATION_CANDIDATE",
            ],
        )
    )

    newly_relevant = discovery.get("newly_relevant_for_b006")
    if not isinstance(newly_relevant, list):
        raise SystemExit("newly_relevant_for_b006 must be an array")
    for repo_id in ("LiquidAI/LFM2.5-1.2B-Base", "Qwen/Qwen3.5-0.8B-Base"):
        _append_unique(newly_relevant, repo_id)

    conclusions = discovery.get("b005_conclusions")
    if not isinstance(conclusions, list):
        raise SystemExit("b005_conclusions must be an array")
    _append_unique(
        conclusions,
        "A canonical 2026-08-27 refresh found two additional compact serious-review cells: LiquidAI/LFM2.5-1.2B-Base and Qwen/Qwen3.5-0.8B-Base; both require B006 classification rather than discovery-time admission.",
    )
    _append_unique(
        conclusions,
        "GLM-5.3-Flash and Kimi-K2-Base are useful frontier coding/agentic references but are screened out before B006 qualification by the universal-laptop product-scale gate (320B/18B active and 1T/32B active respectively).",
    )
    _append_unique(
        conclusions,
        "Current public metadata API revision identity was refreshed for every discovery row; revision drift is explicitly flagged rather than silently retaining stale upstream main identities.",
    )

    discovery["canonical_main_sha"] = EXPECTED_MAIN
    discovery["observed_at_utc"] = "2026-08-27"
    _write_compact_json(discovery_path, discovery)

    binding = _read_json(binding_path)
    if binding.get("task_id") != "B005":
        raise SystemExit("unexpected B005 input-binding identity")
    authority = binding.get("authority")
    if not isinstance(authority, dict) or authority.get("creates_model_access_authority") is not False:
        raise SystemExit("B005 input binding authority invariant is not fail-closed")
    binding["canonical_main_sha"] = EXPECTED_MAIN
    for entry in binding.get("canonical_inputs", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise SystemExit("invalid canonical input entry")
        entry["blob_sha"] = _git_blob(root, entry["path"])
    _write_compact_json(binding_path, binding)

    changed_existing = [row for row in refresh_rows if row[1] != row[2]]
    evidence = evidence_path.read_text(encoding="utf-8")
    marker = "## Closeout state\n"
    if evidence.count(marker) != 1:
        raise SystemExit("B005 closeout marker count is not exactly one")

    drift_lines = []
    for repo_id, old_sha, new_sha, license_tag, gated in changed_existing:
        drift_lines.append(
            f"- `{repo_id}`: `{old_sha or 'UNRESOLVED'}` -> `{new_sha}`; public metadata license tag `{license_tag}`; gated `{gated}`."
        )
    if not drift_lines:
        drift_lines.append("- No previously recorded row changed exact upstream `main` revision during this refresh.")

    refresh = f"""## Canonical current-state refresh — 2026-08-27

This refresh is executed only because the historical B005 implementation predates the canonical B002/B003 machine-gate enforcement and its canonical-input binding no longer matches current `main`. It does not replace the historical evidence; it rebinds B005 to current canonical repository inputs and current public upstream metadata before closeout.

### Exact-main entry gate

```text
ENTRY_GATE_TASK = B005
ENTRY_GATE_CANONICAL_MAIN = {EXPECTED_MAIN}
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_RUN = {ENTRY_GATE_RUN}
ENTRY_GATE_JOB = {ENTRY_GATE_JOB}
```

The entry-gate run also proved B004 terminal, canonical task drift clean, and the frozen repository gates green on the same exact canonical main.

### Refresh boundary

```text
PUBLIC_METADATA_ENDPOINT_CLASS = huggingface.co/api/models/<repo>
MODEL_WEIGHT_ACCESS = NONE
MODEL_FILE_RESOLVE_OR_DOWNLOAD = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
MODEL_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
NEW_AUTHORITY_CREATED = NO
```

The refresh queries only public model metadata and records exact upstream repository revisions. It never calls model-file `resolve` endpoints and never downloads model or tokenizer artifacts.

### Newly serious compact review cells

- `LiquidAI/LFM2.5-1.2B-Base` — exact current revision `{str(lfm['sha']).lower()}`; pre-trained text-only 1.17B base, 32,768 context, on-device-oriented; nonstandard Liquid license metadata requires fail-closed B006 rights review.
- `Qwen/Qwen3.5-0.8B-Base` — exact current revision `{str(qwen['sha']).lower()}`; 0.8B language model, 262,144 native context, Apache-2.0; the card simultaneously says pre-trained-only and `Pre-training & Post-training`, so B006 must reconcile provenance and vision-component cost before primary admission.

Both are added to `newly_relevant_for_b006`. Neither is admitted or authorized for weight access by B005.

### Frontier references screened out before B006 qualification

- `zai-org/GLM-5.3-Flash` — exact current revision `{str(glm['sha']).lower()}`; MIT; 320B total / 18B active; 1,048,576 configured context. Useful coding/agentic reference, but far outside the universal-laptop primary product scale.
- `moonshotai/Kimi-K2-Base` — exact current revision `{str(kimi['sha']).lower()}`; modified MIT; 1T total / 32B active; 131,072 context. It is a foundation checkpoint but is likewise outside the primary product scale.

These rows are discovery references only and are intentionally **not** added to `newly_relevant_for_b006`; no B012 qualification burden or access implication is created for them.

### Existing-row exact-revision revalidation

The refresh re-queried current public metadata for every pre-existing B005 discovery row. When upstream `main` changed, the manifest updates to the exact new SHA and adds `REVISION_DRIFT_SINCE_INITIAL_B005` rather than hiding the drift.

{chr(10).join(drift_lines)}

The refreshed canonical-input binding pins the exact current Git blob SHA for every repository input consumed by B005. Any later drift before merge invalidates the branch and requires re-evaluation.

"""
    evidence_path.write_text(evidence.replace(marker, refresh + marker, 1), encoding="utf-8")

    validation = validation_path.read_text(encoding="utf-8")
    refresh_validation = f"""

## Canonical refresh validation — 2026-08-27

The historical instance identities above remain evidence for PR #41. The canonical B005 refresh supersedes those *instance* blobs for current closeout purposes while retaining the same two task-local Draft 2020-12 schemas.

```text
REFRESH_CANONICAL_MAIN = {EXPECTED_MAIN}
REFRESH_ENTRY_GATE_RUN = {ENTRY_GATE_RUN}
REFRESH_ENTRY_GATE_JOB = {ENTRY_GATE_JOB}
PUBLIC_METADATA_NETWORK = huggingface.co/api/models/<repo> ONLY
MODEL_WEIGHT_ACCESS = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
GATED_TERMS_ACCEPTANCE = NONE
```

The guarded refresh workflow MUST, before pushing its candidate head:

1. self-check both Draft 2020-12 schemas;
2. validate both refreshed JSON instances;
3. reject negative mutations that set `scope.model_weight_access=true` or `authority.creates_model_access_authority=true`;
4. verify every canonical-input Git blob against exact canonical main;
5. run the frozen repository quality gates.

The exact refresh-head qualification and merge identities are intentionally recorded later in B005 canonical closeout evidence, not preclaimed here.
"""
    if "## Canonical refresh validation — 2026-08-27" in validation:
        raise SystemExit("B005 schema validation already contains refresh section")
    validation_path.write_text(validation.rstrip() + refresh_validation + "\n", encoding="utf-8")

    print(f"B005_REFRESH_CANONICAL_MAIN={EXPECTED_MAIN}")
    print(f"B005_REFRESH_EXISTING_ROWS={len(refresh_rows)}")
    print(f"B005_REFRESH_EXISTING_REVISION_DRIFT={len(changed_existing)}")
    for repo_id in required_new:
        payload = metadata[repo_id]
        print(
            "B005_REFRESH_NEW="
            + repo_id
            + ":"
            + str(payload["sha"]).lower()
            + ":license="
            + _license_tag(payload)
            + ":gated="
            + _gated_value(payload)
        )


if __name__ == "__main__":
    main()
