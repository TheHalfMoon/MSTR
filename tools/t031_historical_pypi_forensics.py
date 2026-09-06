#!/usr/bin/env python3
"""Reconstruct the latest compatible wheel closure visible at the original T029 install cutoff.

This tool performs package-metadata/package-wheel access only. It never accesses model repositories,
model files, paid APIs, or training resources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
import venv
import zipfile
from collections import defaultdict, deque
from datetime import datetime, timezone
from email.parser import Parser
from pathlib import Path
from typing import Any

from pip._vendor.packaging.markers import default_environment
from pip._vendor.packaging.requirements import Requirement
from pip._vendor.packaging.specifiers import SpecifierSet
from pip._vendor.packaging.tags import Tag, sys_tags
from pip._vendor.packaging.utils import canonicalize_name, parse_wheel_filename
from pip._vendor.packaging.version import InvalidVersion, Version

CUTOFF = datetime(2026, 8, 26, 10, 44, 6, tzinfo=timezone.utc)
PYTHON_VERSION = Version("3.11.16")
DIRECT = [
    "numpy",
    "torch",
    "sentencepiece",
    "protobuf",
    "gguf",
    "safetensors",
    "transformers",
]
PYPI_HOST = "pypi.org"
FILES_HOST = "files.pythonhosted.org"
USER_AGENT = "mstr-t031-historical-pypi-forensics/1"


def _request_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        final_host = urllib.parse.urlparse(response.geturl()).hostname
        if final_host != PYPI_HOST:
            raise RuntimeError(f"unexpected metadata host: {final_host!r}")
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError(f"unexpected JSON root for {url}")
    return payload


def _download(url: str, destination: Path, expected_sha256: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {PYPI_HOST, FILES_HOST}:
        raise RuntimeError(f"package URL outside no-model allowlist: {url}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    digest = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=120) as response, destination.open("wb") as handle:
        final = urllib.parse.urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in {PYPI_HOST, FILES_HOST}:
            raise RuntimeError(f"package redirect outside no-model allowlist: {response.geturl()}")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"wheel hash mismatch for {destination.name}: {actual} != {expected_sha256}")


def _uploaded_before_cutoff(file_info: dict[str, Any]) -> bool:
    raw = file_info.get("upload_time_iso_8601") or file_info.get("upload_time")
    if not isinstance(raw, str):
        return False
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed <= CUTOFF


def _python_compatible(file_info: dict[str, Any]) -> bool:
    raw = file_info.get("requires_python")
    if raw in (None, ""):
        return True
    try:
        return PYTHON_VERSION in SpecifierSet(str(raw))
    except Exception:
        return False


def _best_compatible_wheel(files: list[dict[str, Any]], tag_rank: dict[Tag, int]) -> dict[str, Any] | None:
    candidates: list[tuple[int, str, dict[str, Any]]] = []
    for item in files:
        if item.get("packagetype") != "bdist_wheel" or item.get("yanked"):
            continue
        if not _uploaded_before_cutoff(item) or not _python_compatible(item):
            continue
        filename = item.get("filename")
        if not isinstance(filename, str):
            continue
        try:
            _, _, _, wheel_tags = parse_wheel_filename(filename)
        except Exception:
            continue
        ranks = [tag_rank[tag] for tag in wheel_tags if tag in tag_rank]
        if not ranks:
            continue
        candidates.append((min(ranks), filename, item))
    if not candidates:
        return None
    candidates.sort(key=lambda row: (row[0], row[1]))
    return candidates[0][2]


def _select_release(
    name: str,
    specifiers: list[SpecifierSet],
    metadata: dict[str, Any],
    tag_rank: dict[Tag, int],
) -> tuple[Version, dict[str, Any]]:
    releases = metadata.get("releases")
    if not isinstance(releases, dict):
        raise RuntimeError(f"PyPI releases missing for {name}")
    choices: list[tuple[Version, dict[str, Any]]] = []
    for raw_version, files in releases.items():
        try:
            version = Version(raw_version)
        except InvalidVersion:
            continue
        if version.is_prerelease or version.is_devrelease:
            continue
        if any(version not in spec for spec in specifiers):
            continue
        if not isinstance(files, list):
            continue
        wheel = _best_compatible_wheel(files, tag_rank)
        if wheel is not None:
            choices.append((version, wheel))
    if not choices:
        rendered = ",".join(str(s) for s in specifiers) or "<any>"
        raise RuntimeError(f"no compatible pre-cutoff wheel for {name} satisfying {rendered}")
    choices.sort(key=lambda pair: pair[0], reverse=True)
    return choices[0]


def _wheel_requires_dist(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise RuntimeError(f"expected one METADATA in {path.name}, found {len(metadata_names)}")
        text = archive.read(metadata_names[0]).decode("utf-8", errors="replace")
    message = Parser().parsestr(text)
    return list(message.get_all("Requires-Dist") or [])


def _marker_applies(requirement: Requirement) -> bool:
    if requirement.marker is None:
        return True
    env = default_environment()
    env.update(
        {
            "python_full_version": "3.11.16",
            "python_version": "3.11",
            "implementation_name": "cpython",
            "platform_system": "Linux",
            "sys_platform": "linux",
            "extra": "",
        }
    )
    return bool(requirement.marker.evaluate(env))


def reconstruct(workdir: Path) -> dict[str, Any]:
    tags = list(sys_tags())
    tag_rank = {tag: index for index, tag in enumerate(tags)}
    pypi_cache: dict[str, dict[str, Any]] = {}
    constraints: dict[str, list[SpecifierSet]] = defaultdict(list)
    display_names: dict[str, str] = {}
    selected: dict[str, dict[str, Any]] = {}
    wheelhouse = workdir / "wheelhouse"
    wheelhouse.mkdir(parents=True, exist_ok=True)

    for name in DIRECT:
        canonical = canonicalize_name(name)
        display_names[canonical] = name
        constraints[canonical].append(SpecifierSet())

    queue: deque[str] = deque(constraints)
    iterations = 0
    while queue:
        iterations += 1
        if iterations > 1000:
            raise RuntimeError("resolver did not converge")
        canonical = queue.popleft()
        name = display_names.get(canonical, canonical)
        metadata = pypi_cache.get(canonical)
        if metadata is None:
            metadata = _request_json(f"https://pypi.org/pypi/{name}/json")
            pypi_cache[canonical] = metadata
        version, file_info = _select_release(name, constraints[canonical], metadata, tag_rank)
        filename = str(file_info["filename"])
        expected_sha = str(file_info["digests"]["sha256"])
        prior = selected.get(canonical)
        if prior and prior["version"] == str(version) and prior["filename"] == filename:
            continue

        destination = wheelhouse / filename
        if not destination.exists():
            _download(str(file_info["url"]), destination, expected_sha)
        else:
            actual = hashlib.sha256(destination.read_bytes()).hexdigest()
            if actual != expected_sha:
                raise RuntimeError(f"cached wheel hash mismatch: {filename}")

        selected[canonical] = {
            "name": name,
            "version": str(version),
            "filename": filename,
            "url": str(file_info["url"]),
            "sha256": expected_sha,
            "upload_time_iso_8601": file_info.get("upload_time_iso_8601"),
            "requires_python": file_info.get("requires_python"),
            "size_bytes": destination.stat().st_size,
        }

        for raw_req in _wheel_requires_dist(destination):
            req = Requirement(raw_req)
            if req.extras or not _marker_applies(req):
                continue
            dep = canonicalize_name(req.name)
            display_names.setdefault(dep, req.name)
            new_spec = req.specifier
            rendered = str(new_spec)
            if all(str(existing) != rendered for existing in constraints[dep]):
                constraints[dep].append(new_spec)
                queue.append(dep)

        for dep in list(selected):
            if dep not in constraints:
                continue
            selected_version = Version(str(selected[dep]["version"]))
            if any(selected_version not in spec for spec in constraints[dep]):
                queue.append(dep)

    venv_dir = workdir / "venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
    python_exe = venv_dir / "bin" / "python"
    wheel_paths = [str(wheelhouse / selected[name]["filename"]) for name in sorted(selected)]
    install = subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--no-index", "--no-deps", *wheel_paths],
        check=False,
        capture_output=True,
        text=True,
        timeout=900,
    )
    if install.returncode != 0:
        raise RuntimeError(f"historical wheel install failed:\n{install.stdout}\n{install.stderr}")
    check = subprocess.run(
        [str(python_exe), "-m", "pip", "check"],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if check.returncode != 0:
        raise RuntimeError(f"historical closure pip check failed:\n{check.stdout}\n{check.stderr}")
    freeze = subprocess.run(
        [str(python_exe), "-m", "pip", "freeze", "--all"],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    ).stdout.splitlines()

    return {
        "schema_version": "mstr.t031-historical-pypi-forensics.v1",
        "task_id": "T031",
        "historical_install_cutoff_utc": CUTOFF.isoformat().replace("+00:00", "Z"),
        "source_t029_run_id": 32959729068,
        "source_t029_head": "406de41d132fa6d24d55814f3f6dd4fced5f12bd",
        "python_version": "3.11.16",
        "selection_semantics": "latest stable compatible non-yanked wheel whose upload timestamp is at or before the original pip-install cutoff; dependency metadata recursively resolved with original no-extra marker environment",
        "direct_requirement_names": DIRECT,
        "direct_selected_versions": {name: selected[canonicalize_name(name)]["version"] for name in DIRECT},
        "package_count": len(selected),
        "packages": [selected[name] for name in sorted(selected)],
        "pip_check": check.stdout.strip(),
        "pip_freeze_all": freeze,
        "model_access": "NONE",
        "training": False,
        "paid_cost_usd": 0.0,
        "network_hosts": [PYPI_HOST, FILES_HOST],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    args.workdir.mkdir(parents=True, exist_ok=True)
    report = reconstruct(args.workdir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "package_count": report["package_count"],
        "direct_selected_versions": report["direct_selected_versions"],
        "model_access": "NONE",
        "training": False,
        "paid_cost_usd": 0.0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
