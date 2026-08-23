"""Manifest-driven static site staging."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml


def stage_site(project_root: str | Path, destination: str | Path | None = None) -> Path:
    root = Path(project_root).resolve()
    manifest_path = root / "apps" / "web" / "site-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("site manifest schema_version must be 1")
    target = Path(destination).resolve() if destination else root / "_site"
    if target == root or root not in target.parents:
        raise ValueError("site destination must be a child of the project root")
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    public_root = (root / manifest["public_root"]).resolve()
    if not public_root.is_dir():
        raise FileNotFoundError(f"public root not found: {public_root}")
    shutil.copytree(public_root, target, dirs_exist_ok=True)

    for relative in manifest.get("files", []):
        source = root / relative
        output = target / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, output)
    for pattern in manifest.get("document_patterns", []):
        for source in root.glob(pattern):
            if not source.is_file():
                continue
            output = target / source.relative_to(root)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, output)
    return target
