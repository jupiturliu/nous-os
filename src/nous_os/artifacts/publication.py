"""Explicit publication of privacy-filtered runtime Projections."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from nous_os.core.runtime import RuntimePaths


PRIVATE_PATTERN = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|"
    r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b|"
    r"\b\d{3}-\d{2}-\d{4}\b",
    re.I,
)


def publish_site_data(paths: RuntimePaths, site_public: str | Path) -> tuple[Path, Path]:
    public = Path(site_public).resolve()
    dashboard = paths.projections / "dashboard-data.json"
    latest = paths.projections / "research-records" / "latest.json"
    for source in (dashboard, latest):
        if not source.exists():
            raise FileNotFoundError(f"runtime projection not found: {source}")
        payload = json.loads(source.read_text(encoding="utf-8"))
        _validate_public_payload(payload, source)
    dashboard_target = public / "examples" / "runtime" / "dashboard-data.json"
    research_target = public / "examples" / "runtime" / "research-records" / "latest.json"
    dashboard_target.parent.mkdir(parents=True, exist_ok=True)
    research_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dashboard, dashboard_target)
    shutil.copy2(latest, research_target)
    return dashboard_target, research_target


def _validate_public_payload(value, source: Path) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if any(token in key.lower() for token in ("secret", "password", "api_key", "token")):
                raise ValueError(f"private key {key!r} cannot be published from {source}")
            _validate_public_payload(item, source)
    elif isinstance(value, list):
        for item in value:
            _validate_public_payload(item, source)
    elif isinstance(value, str):
        if PRIVATE_PATTERN.search(value):
            raise ValueError(f"private text pattern cannot be published from {source}")
        if value.startswith(("/Users/", "/home/", "file://")):
            raise ValueError(f"local filesystem path cannot be published from {source}")
