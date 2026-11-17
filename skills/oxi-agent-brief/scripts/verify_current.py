#!/usr/bin/env python3
"""Verify that the discoverable skill exactly matches CURRENT.json."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


IGNORED_DIRS = {"__pycache__", ".git"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        result[relative.as_posix()] = sha256_file(path)
    return result


def main() -> int:
    skill_dir = Path(__file__).resolve().parent.parent
    versions_root = skill_dir.parent / "_versions" / skill_dir.name
    current = json.loads((versions_root / "CURRENT.json").read_text(encoding="utf-8"))
    snapshot = versions_root / current["snapshot_path"]
    version = json.loads((snapshot / "VERSION.json").read_text(encoding="utf-8"))

    active_manifest = manifest(skill_dir)
    expected_manifest = version["files"]
    if active_manifest != expected_manifest:
        active_names = set(active_manifest)
        expected_names = set(expected_manifest)
        changed = sorted(
            name
            for name in active_names & expected_names
            if active_manifest[name] != expected_manifest[name]
        )
        print(json.dumps({
            "active_version": current["active_version"],
            "changed": changed,
            "extra": sorted(active_names - expected_names),
            "missing": sorted(expected_names - active_names),
            "status": "mismatch",
        }, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({
        "active_version": current["active_version"],
        "files": len(active_manifest),
        "status": "validated-match",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
