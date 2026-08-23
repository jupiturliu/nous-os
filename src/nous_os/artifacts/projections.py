"""Deterministic Projections reconstructed from Evidence Events."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from nous_os.core.events import EventStore


def project_latest_heartbeat(store: EventStore) -> tuple[Path, Path]:
    events = [event for event in store.events() if event.get("event_type") == "heartbeat.completed"]
    if not events:
        raise ValueError("no heartbeat.completed Evidence Event is available")
    event = events[-1]
    references = event.get("evidence_refs") or []
    if not references:
        raise ValueError("heartbeat event has no snapshot Artifact reference")
    reference = references[0]
    artifact_path = (store.paths.home / reference["path"]).resolve()
    if store.paths.home != artifact_path and store.paths.home not in artifact_path.parents:
        raise ValueError("artifact reference escapes Runtime Home")
    encoded = artifact_path.read_bytes()
    if hashlib.sha256(encoded).hexdigest() != reference["sha256"]:
        raise ValueError("heartbeat Artifact hash does not match Evidence Event")
    snapshot = json.loads(encoded)
    record = snapshot["research_record"]
    dashboard_path = store.paths.projections / "dashboard-data.json"
    research_dir = store.paths.projections / "research-records"
    record_path = research_dir / f"{record['run_id']}.json"
    latest_path = research_dir / "latest.json"
    _atomic_json(dashboard_path, snapshot)
    _atomic_json(record_path, record)
    _atomic_json(latest_path, record)
    return dashboard_path, latest_path


def _atomic_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded)
    os.chmod(temporary, 0o600)
    temporary.replace(path)
