"""Non-overwriting, checksum-verified experiment backups and restores."""
from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_child(root, relative):
    candidate = (root / relative).resolve()
    candidate.relative_to(root.resolve())
    return candidate


def create_backup(sources, destination_root, *, label="ecuador"):
    """Copy explicit model/run/metric directories into a unique snapshot."""
    if not sources:
        raise ValueError("Provide explicitly named experiment directories.")
    destination_root = Path(destination_root).expanduser().resolve()
    existing, missing = {}, {}
    for name, source in sources.items():
        if not name or Path(name).name != name or name in {".", ".."}:
            raise ValueError("Backup source names must be single directory names.")
        source = Path(source).expanduser().resolve()
        if source.exists():
            if not source.is_dir():
                raise ValueError(f"Expected a directory: {source}")
            if destination_root == source or source in destination_root.parents:
                raise ValueError("The destination cannot be inside a source directory.")
            if any(p.is_symlink() for p in source.rglob("*")):
                raise ValueError("Experiment backups do not follow symbolic links.")
            existing[name] = source
        else:
            missing[name] = str(source)
    if not existing:
        raise FileNotFoundError("None of the requested experiment directories exist.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = destination_root / f"{label}_{stamp}_{uuid.uuid4().hex[:8]}"
    target.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name, source in existing.items():
        shutil.copytree(source, target/name)
        for original in sorted(source.rglob("*")):
            if original.is_file():
                relative = Path(name)/original.relative_to(source)
                expected = _sha256(original)
                if _sha256(target/relative) != expected:
                    raise OSError(f"Backup verification failed: {relative}")
                hashes[relative.as_posix()] = expected
    manifest = {"created_utc": stamp, "sources": {k: str(v) for k, v in existing.items()},
                "missing_sources": missing, "files_sha256": hashes, "file_count": len(hashes)}
    (target/"backup_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    verify_backup(target)
    return target


def verify_backup(directory):
    root = Path(directory).resolve()
    manifest = json.loads((root/"backup_manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["files_sha256"].items():
        path = _safe_child(root, relative)
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError(f"Missing or damaged backup file: {relative}")
    return manifest


def restore_backup(directory, destination):
    source, destination = Path(directory).resolve(), Path(destination).resolve()
    verify_backup(source)
    if destination.exists():
        raise FileExistsError(f"Restore requires a new destination: {destination}")
    if source in destination.parents:
        raise ValueError("Restore destination cannot be inside the backup.")
    shutil.copytree(source, destination)
    verify_backup(destination)
    return destination
