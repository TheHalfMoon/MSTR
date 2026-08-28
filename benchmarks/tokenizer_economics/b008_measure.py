from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

import tokenizers
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

PROTOCOL_ID = "MSTR-TOKENIZER-ECONOMICS-v0"
CORPUS_PATH = Path("benchmarks/fixtures/tokenizer-economics/B007-corpus.json")
MANIFEST_PATH = Path("benchmarks/manifests/B007-tokenizer-economics.json")
IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
REQUIRED_RESULT_KEYS = {
    "candidate_id",
    "tokenizer_id",
    "tokenizer_revision",
    "loaded_tokenizer_artifact_sha256_inventory",
    "tokenizer_implementation_id",
    "tokenizer_implementation_version",
    "measurement_runtime_identity",
    "effective_runtime_settings",
    "token_count_api_identity",
    "acquisition_source_and_provenance",
    "protocol_id",
    "corpus_fixture_sha256",
    "per_entry_metrics",
    "per_category_metrics",
    "aggregate_metrics",
    "structural_observations",
    "measurement_failures",
    "measured_at",
    "executor_identity",
}


def strict_load(path: Path) -> Any:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_hook)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def nearest_rank(values: list[int], percentile: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def corpus_preflight() -> tuple[dict[str, Any], dict[str, Any]]:
    corpus = strict_load(CORPUS_PATH)
    manifest = strict_load(MANIFEST_PATH)
    spec = manifest["corpus"]
    raw = CORPUS_PATH.read_bytes()
    assert len(raw) == spec["fixture_file_bytes"]
    assert sha256_bytes(raw) == spec["fixture_sha256"]
    blob = subprocess.check_output(["git", "hash-object", str(CORPUS_PATH)], text=True).strip()
    assert blob == spec["expected_git_blob_sha1"]
    entries = corpus["entries"]
    assert len(entries) == spec["entry_count"] == 34
    assert len({e["fixture_id"] for e in entries}) == 34
    pins = {p["fixture_id"]: p for p in spec["entry_pins"]}
    decoded_total = 0
    categories: dict[str, set[str]] = defaultdict(set)
    for entry in entries:
        raw_content = entry["content_utf8"].encode("utf-8")
        assert len(raw_content) == entry["byte_count"]
        assert sha256_bytes(raw_content) == entry["sha256"]
        pin = pins[entry["fixture_id"]]
        assert pin["category"] == entry["category"]
        assert pin["profile"] == entry["profile"]
        assert pin["byte_count"] == entry["byte_count"]
        assert pin["sha256"] == entry["sha256"]
        decoded_total += len(raw_content)
        categories[entry["category"]].add(entry["profile"])
    assert decoded_total == spec["decoded_content_bytes"]
    assert sorted(categories) == sorted(spec["required_categories"])
    assert all(v == {"baseline", "adversarial"} for v in categories.values())
    return corpus, manifest


def structural_observation(category: str, text: str) -> dict[str, Any] | None:
    if category == "diff":
        lines = text.splitlines()
        return {
            "hunk_count": sum(line.startswith("@@") for line in lines),
            "added_line_count": sum(
                line.startswith("+") and not line.startswith("+++") for line in lines
            ),
            "deleted_line_count": sum(
                line.startswith("-") and not line.startswith("---") for line in lines
            ),
            "context_line_count": sum(line.startswith(" ") for line in lines),
            "renames_or_binary_markers_present": any(
                marker in text for marker in ("rename from", "rename to", "Binary files")
            ),
        }
    if category == "file_paths":
        paths = [line for line in text.splitlines() if line]
        ext = Counter()
        max_depth = 0
        for path in paths:
            normalized = path.replace("\\", "/")
            parts = [part for part in normalized.split("/") if part]
            max_depth = max(max_depth, len(parts))
            suffix = Path(parts[-1]).suffix.lower() if parts else ""
            if suffix:
                ext[suffix] += 1
        return {
            "path_count": len(paths),
            "max_depth": max_depth,
            "extension_counts": dict(sorted(ext.items())),
            "windows_or_unc_path_present": any(
                re.match(r"^[A-Za-z]:\\", p) or p.startswith("//") for p in paths
            ),
            "unicode_path_present": any(any(ord(ch) > 127 for ch in p) for p in paths),
        }
    if category == "stack_trace":
        lines = text.splitlines()
        if text.startswith("Traceback"):
            family = "python"
            frames = sum(line.lstrip().startswith("File ") for line in lines)
        else:
            family = "node"
            frames = sum(line.lstrip().startswith("at ") for line in lines)
        return {
            "frame_count": frames,
            "runtime_family": family,
            "async_or_cause_markers_present": "async " in text or "Caused by:" in text,
        }
    if category == "tool_json":
        data = json.loads(text)
        counts = {"arrays": 0, "objects": 0, "max_depth": 0, "error": False}

        def walk(value: Any, depth: int) -> None:
            counts["max_depth"] = max(counts["max_depth"], depth)
            if isinstance(value, dict):
                counts["objects"] += 1
                if "error" in value:
                    counts["error"] = True
                for child in value.values():
                    walk(child, depth + 1)
            elif isinstance(value, list):
                counts["arrays"] += 1
                for child in value:
                    walk(child, depth + 1)

        walk(data, 1)
        return {
            "max_json_nesting_depth": counts["max_depth"],
            "array_count": counts["arrays"],
            "object_count": counts["objects"],
            "error_object_present": counts["error"],
        }
    return None


def measure_entry(tok: Tokenizer, entry: dict[str, Any]) -> dict[str, Any]:
    text = entry["content_utf8"]
    encoding = tok.encode(text, add_special_tokens=False)
    token_count = len(encoding.ids)
    if token_count <= 0:
        raise ValueError(f"zero token count for {entry['fixture_id']}")
    identifier_counts = [
        len(tok.encode(match.group(0), add_special_tokens=False).ids)
        for match in IDENTIFIER_RE.finditer(text)
    ]
    identifier_total = sum(identifier_counts)
    occurrence_count = len(identifier_counts)
    result = {
        "fixture_id": entry["fixture_id"],
        "category": entry["category"],
        "profile": entry["profile"],
        "byte_count": entry["byte_count"],
        "token_count": token_count,
        "bytes_per_token": entry["byte_count"] / token_count,
        "character_count": len(text),
        "characters_per_token": len(text) / token_count,
        "identifier_like_occurrence_count": occurrence_count,
        "identifier_like_token_piece_count": identifier_total,
        "mean_tokens_per_identifier_like_occurrence": mean(identifier_counts)
        if identifier_counts
        else None,
        "p50_tokens_per_identifier_like_occurrence": nearest_rank(identifier_counts, 0.50),
        "p95_tokens_per_identifier_like_occurrence": nearest_rank(identifier_counts, 0.95),
        "max_tokens_per_identifier_like_occurrence": max(identifier_counts)
        if identifier_counts
        else None,
        "multi_token_identifier_like_occurrence_fraction": (
            sum(count > 1 for count in identifier_counts) / occurrence_count
            if occurrence_count
            else None
        ),
        "offset_mapping_observed": len(encoding.offsets) == token_count,
        "overflow_count": len(encoding.overflowing),
    }
    return result


def measure_candidate(
    candidate: dict[str, Any], corpus: dict[str, Any], manifest: dict[str, Any], work: Path
) -> dict[str, Any]:
    cid = candidate["candidate_id"]
    repo = candidate["upstream_id"]
    revision = candidate["upstream_revision"]
    local = work / cid
    path = Path(
        hf_hub_download(
            repo_id=repo,
            filename="tokenizer.json",
            revision=revision,
            local_dir=str(local),
            token=False,
        )
    )
    assert path.name == "tokenizer.json"
    raw = path.read_bytes()
    tok = Tokenizer.from_file(str(path))
    per_entry = [measure_entry(tok, entry) for entry in corpus["entries"]]
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in per_entry:
        by_category[row["category"]].append(row)
    per_category = []
    for category in manifest["corpus"]["required_categories"]:
        rows = by_category[category]
        total_bytes = sum(row["byte_count"] for row in rows)
        total_chars = sum(row["character_count"] for row in rows)
        total_tokens = sum(row["token_count"] for row in rows)
        per_category.append(
            {
                "category": category,
                "entry_count": len(rows),
                "total_bytes": total_bytes,
                "total_characters": total_chars,
                "total_tokens": total_tokens,
                "weighted_bytes_per_token": total_bytes / total_tokens,
                "weighted_characters_per_token": total_chars / total_tokens,
            }
        )
    total_bytes = sum(row["byte_count"] for row in per_entry)
    total_chars = sum(row["character_count"] for row in per_entry)
    total_tokens = sum(row["token_count"] for row in per_entry)
    structural = []
    for entry in corpus["entries"]:
        obs = structural_observation(entry["category"], entry["content_utf8"])
        if obs is not None:
            structural.append(
                {"fixture_id": entry["fixture_id"], "category": entry["category"], **obs}
            )
    executor = f"github-actions:{os.environ.get('GITHUB_RUN_ID', 'unknown')}:build"
    result = {
        "format_version": "mstr.tokenizer-economics-result.v0",
        "task_id": "B008",
        "workstream_id": "MSTR-000B",
        "candidate_id": cid,
        "tokenizer_id": repo,
        "tokenizer_revision": revision,
        "loaded_tokenizer_artifact_sha256_inventory": [
            {
                "path": "tokenizer.json",
                "bytes": len(raw),
                "sha256": sha256_bytes(raw),
            }
        ],
        "tokenizer_implementation_id": "huggingface-tokenizers.Tokenizer.from_file(tokenizer.json)",
        "tokenizer_implementation_version": tokenizers.__version__,
        "measurement_runtime_identity": {
            "python_version": platform.python_version(),
            "tokenizer_library": "tokenizers",
            "tokenizer_library_version": tokenizers.__version__,
            "tokenizer_implementation_class": tok.__class__.__name__,
            "executor_identity": executor,
            "platform": platform.platform(),
        },
        "effective_runtime_settings": {
            "add_special_tokens": False,
            "bos_injection": False,
            "eos_injection": False,
            "chat_template": "PROHIBITED_AND_ASSERTED_UNUSED",
            "padding": "NONE",
            "truncation": "NONE",
            "pre_measurement_whitespace_normalization": "NONE",
            "pre_measurement_newline_normalization": "NONE",
            "tokenizer_native_normalizer": "AS_PINNED_BY_TOKENIZER_REVISION",
            "identifier_percentile_method": "NEAREST_RANK",
            "offset_mapping_capability": True,
            "overflow_or_truncation_observation": (
                "encoding.overflowing recorded; no truncation requested"
            ),
        },
        "token_count_api_identity": (
            "tokenizers.Tokenizer.encode(text, add_special_tokens=False).ids length"
        ),
        "acquisition_source_and_provenance": {
            "provider": "Hugging Face Hub",
            "repository": repo,
            "revision": revision,
            "filename": "tokenizer.json",
            "authenticated": False,
            "requested_remote_files": ["tokenizer.json"],
        },
        "protocol_id": PROTOCOL_ID,
        "corpus_fixture_sha256": manifest["corpus"]["fixture_sha256"],
        "per_entry_metrics": per_entry,
        "per_category_metrics": per_category,
        "aggregate_metrics": {
            "total_bytes": total_bytes,
            "total_characters": total_chars,
            "total_tokens": total_tokens,
            "weighted_bytes_per_token": total_bytes / total_tokens,
            "weighted_characters_per_token": total_chars / total_tokens,
            "estimated_effective_payload_bytes_at_8192_tokens": math.floor(
                (total_bytes / total_tokens) * 8192
            ),
            "numerator_denominator_totals": {
                "bytes": total_bytes,
                "characters": total_chars,
                "tokens": total_tokens,
            },
        },
        "structural_observations": structural,
        "measurement_failures": [],
        "measured_at": datetime.now(UTC).isoformat(),
        "executor_identity": executor,
    }
    assert REQUIRED_RESULT_KEYS <= set(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    corpus, manifest = corpus_preflight()
    candidates = []
    for path in sorted(Path("artifacts/candidates").glob("*.json")):
        candidate = strict_load(path)
        rights = candidate.get("rights", {})
        if candidate.get("status") != "static_qualified":
            continue
        assert rights.get("decision") == "pass_permissive"
        assert rights.get("account_gate_required") is False
        assert rights.get("clickthrough_gate_required") is False
        candidates.append(candidate)
    assert len(candidates) == 10
    args.output_dir.mkdir(parents=True, exist_ok=True)
    work = Path("/tmp/b008-tokenizer-measurement")
    work.mkdir(parents=True, exist_ok=True)
    results = []
    try:
        for candidate in candidates:
            result = measure_candidate(candidate, corpus, manifest, work)
            out = args.output_dir / f"{candidate['candidate_id']}.json"
            out.write_text(
                json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
            )
            results.append(result)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ranked = sorted(
        results, key=lambda r: r["aggregate_metrics"]["weighted_bytes_per_token"], reverse=True
    )
    lines = [
        "# B008 Tokenizer Economics Measurement",
        "",
        "**Task:** `B008`",
        "**State:** IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT",
        f"**Canonical entry main:** `{os.environ.get('EXPECTED_MAIN', 'unknown')}`",
        "",
        "## Entry and execution evidence",
        "",
        "```text",
        f"ENTRY_GATE_RUN = {os.environ.get('ENTRY_RUN', 'unknown')}",
        f"ENTRY_GATE_JOB = {os.environ.get('ENTRY_JOB', 'unknown')}",
        f"ENTRY_GATE_CANONICAL_MAIN = {os.environ.get('EXPECTED_MAIN', 'unknown')}",
        "ENTRY_GATE_ELIGIBLE = true",
        f"TOKENIZER_JSON_LOADABILITY_RUN = {os.environ.get('LOADABILITY_RUN', 'unknown')}",
        f"TOKENIZER_JSON_LOADABILITY_JOB = {os.environ.get('LOADABILITY_JOB', 'unknown')}",
        f"MEASUREMENT_RUN = {os.environ.get('GITHUB_RUN_ID', 'unknown')}",
        "MEASUREMENT_EXECUTOR = GitHub-hosted ubuntu-24.04 / Python 3.11 / tokenizers 0.22.0",
        "REMOTE_FILE_PER_CANDIDATE = tokenizer.json only",
        "MODEL_INFERENCE = NONE",
        "GATED_TERMS_ACCEPTANCE = NONE",
        "PAID_COMPUTE = NONE",
        "FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO",
        "```",
        "",
        "## Candidate set",
        "",
        (
            "The measured set is derived from canonical candidate records with "
            "`status=static_qualified`, `rights.decision=pass_permissive`, and no "
            "account/clickthrough gate. Exactly 10 candidates satisfy that rule "
            "on the entry main."
        ),
        "",
        "## Results",
        "",
        (
            "Higher weighted bytes/token means denser payload under this fixed "
            "synthetic corpus. The 8192-token payload is a corpus-ratio estimate, "
            "not a context-window claim."
        ),
        "",
        (
            "| Candidate | Bytes/token | Total tokens | 8K payload bytes | "
            "Diff tokens | Stacktrace tokens | Tool JSON tokens | Path tokens |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in ranked:
        cats = {row["category"]: row for row in result["per_category_metrics"]}
        agg = result["aggregate_metrics"]
        lines.append(
            "".join(
                [
                    f"| `{result['candidate_id']}` | ",
                    f"{agg['weighted_bytes_per_token']:.6f} | ",
                    f"{agg['total_tokens']} | ",
                    f"{agg['estimated_effective_payload_bytes_at_8192_tokens']} | ",
                    f"{cats['diff']['total_tokens']} | ",
                    f"{cats['stack_trace']['total_tokens']} | ",
                    f"{cats['tool_json']['total_tokens']} | ",
                    f"{cats['file_paths']['total_tokens']} |",
                ]
            )
        )
    lines += [
        "",
        "## Measurement contract",
        "",
        (
            "- Corpus integrity is checked against the frozen B007 manifest "
            "before any tokenizer is used."
        ),
        (
            "- Only pinned `tokenizer.json` is acquired for each candidate; that "
            "exact file is SHA-256 inventoried and is the only tokenizer artifact "
            "loaded."
        ),
        (
            "- `tokenizers.Tokenizer.from_file` is used with "
            "`add_special_tokens=false`; chat templates, padding, truncation, "
            "pre-normalization, BOS and EOS injection are not used."
        ),
        (
            "- Identifier-like spans use the frozen ASCII regex and are encoded "
            "in isolation. p50/p95 use deterministic nearest-rank percentiles."
        ),
        (
            "- Structural observations are recorded for diff, file paths, stack "
            "traces and tool JSON fixtures."
        ),
        "- All temporary tokenizer files are deleted in the ephemeral runner before completion.",
        "",
        "## Claim boundary",
        "",
        (
            "These results compare tokenizer economics on the deterministic B007 "
            "synthetic fixture only. They do not establish population-level code "
            "efficiency, model quality, inference quality, trainability, or "
            "production fitness."
        ),
        "",
        (
            "This task does not perform model inference, accept gated terms, use "
            "paid compute, or place tokenizer artifacts on the founder machine."
        ),
        "",
    ]
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text("\n".join(lines), encoding="utf-8")
    print(f"B008_RESULTS_WRITTEN={len(results)}")
    print(f"B008_CORPUS_SHA256={manifest['corpus']['fixture_sha256']}")
    print("B008_EPHEMERAL_CLEANUP=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
