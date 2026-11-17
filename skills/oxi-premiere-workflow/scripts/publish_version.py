#!/usr/bin/env python3
"""Publish one validated snapshot of oxi-premiere-workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


VERSION_RE = re.compile(r"^(?P<date>\d{8})-v(?P<number>\d{3})$")
IGNORED_DIRS = {"__pycache__", ".git"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_under(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        yield path, relative


def find_validator(explicit: str | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.append(
        Path.home()
        / ".codex"
        / "skills"
        / ".system"
        / "skill-creator"
        / "scripts"
        / "quick_validate.py"
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "Không tìm thấy quick_validate.py. Truyền đường dẫn bằng --validator."
    )


def validate(skill_dir: Path, validator: Path) -> None:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(validator), str(skill_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise RuntimeError(f"Skill chưa qua kiểm tra:\n{detail}")


def next_version(versions_root: Path, date_stamp: str) -> str:
    used = []
    for child in versions_root.iterdir():
        if not child.is_dir():
            continue
        match = VERSION_RE.match(child.name)
        if match and match.group("date") == date_stamp:
            used.append(int(match.group("number")))
    number = max(used, default=0) + 1
    if number > 999:
        raise RuntimeError(f"Đã hết số phiên bản cho ngày {date_stamp}")
    return f"{date_stamp}-v{number:03d}"


def find_sync_conflicts(versions_root: Path) -> list[Path]:
    conflicts = []
    for path in versions_root.rglob("*"):
        relative = path.relative_to(versions_root)
        if any("sync-conflict" in part.lower() for part in relative.parts):
            conflicts.append(path)
    return sorted(conflicts)


def is_reparse_point(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & 0x400)


def prune_superseded_versions(versions_root: Path, active_version: str) -> list[str]:
    root = versions_root.resolve()
    candidates = [
        child
        for child in versions_root.iterdir()
        if child.is_dir()
        and VERSION_RE.match(child.name)
        and child.name != active_version
    ]

    for child in candidates:
        if is_reparse_point(child) or child.resolve().parent != root:
            raise RuntimeError(
                f"Từ chối dọn đường dẫn không phải thư mục version thường: {child}"
            )

    removed = []
    for child in candidates:
        shutil.rmtree(child)
        removed.append(child.name)
    return sorted(removed)


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and publish a dated immutable skill snapshot."
    )
    default_skill = Path(__file__).resolve().parent.parent
    parser.add_argument("--skill-dir", default=str(default_skill))
    parser.add_argument("--versions-root")
    parser.add_argument("--validator")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not (skill_dir / "SKILL.md").is_file():
        raise FileNotFoundError(f"Không thấy SKILL.md trong {skill_dir}")

    versions_root = (
        Path(args.versions_root).expanduser().resolve()
        if args.versions_root
        else skill_dir.parent / "_versions" / skill_dir.name
    )
    versions_root.mkdir(parents=True, exist_ok=True)

    conflicts = find_sync_conflicts(versions_root)
    if conflicts:
        detail = "\n".join(str(path) for path in conflicts)
        raise RuntimeError(
            "Phát hiện sync-conflict; giữ nguyên mọi file và dừng publish/dọn version:\n"
            + detail
        )

    validator = find_validator(args.validator)
    validate(skill_dir, validator)

    now = datetime.now(timezone.utc)
    version = next_version(versions_root, now.astimezone().strftime("%Y%m%d"))
    final_dir = versions_root / version
    if final_dir.exists():
        raise FileExistsError(f"Phiên bản đã tồn tại: {final_dir}")

    temporary_dir = Path(
        tempfile.mkdtemp(prefix=f".{version}.", dir=versions_root)
    )
    try:
        for source, relative in files_under(skill_dir):
            destination = temporary_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        manifest = {
            relative.as_posix(): sha256_file(path)
            for path, relative in files_under(temporary_dir)
        }
        version_payload = {
            "created_at_utc": now.isoformat(),
            "files": manifest,
            "schema_version": 1,
            "skill": skill_dir.name,
            "source_machine": platform.node(),
            "status": "validated",
            "version": version,
        }
        write_json_atomic(temporary_dir / "VERSION.json", version_payload)
        temporary_dir.rename(final_dir)
    except Exception:
        if temporary_dir.exists():
            shutil.rmtree(temporary_dir)
        raise

    current_payload = {
        "active_skill_path": "../../oxi-premiere-workflow",
        "active_version": version,
        "schema_version": 1,
        "skill": skill_dir.name,
        "snapshot_path": version,
        "status": "validated",
        "validated_at_utc": now.isoformat(),
    }
    write_json_atomic(versions_root / "CURRENT.json", current_payload)

    removed_versions = prune_superseded_versions(versions_root, version)

    result_payload = dict(current_payload)
    result_payload["removed_versions"] = removed_versions
    print(json.dumps(result_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
